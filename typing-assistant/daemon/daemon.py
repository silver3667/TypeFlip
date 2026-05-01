"""Main daemon: clipboard-based hotkey processing.

Workflow: user selects text -> presses hotkey -> daemon copies selection,
processes it, and pastes the result back.
"""

from __future__ import annotations

import os
import sys
import time
import threading
import uuid
from collections.abc import Callable

import keyboard as kb
import pyperclip

from config.settings import OPENAI_API_KEY
from daemon.hotkeys import register_hotkeys
from daemon.log import get_logger, log_path
from processors.layout_converter import convert_auto
from processors.typo_corrector import correct_typos
from tools.registry import TOOLS

# Drop hotkey fires within this window of the last successful start.
# 0.8s clears Windows F1 auto-repeat (which kicks in at ~500ms with held key).
_RATE_LIMIT_S = 0.8
_last_call_at = 0.0
_processing = False
_processing_lock = threading.Lock()

log = get_logger()

# Toggle native Win32 SendInput for ctrl+v instead of keyboard.send. Use this
# to rule out the `keyboard` library as the cause of any double-paste bug.
_USE_NATIVE_PASTE = os.environ.get("TYPING_ASSISTANT_NATIVE_PASTE") == "1"


def _acquire_singleton() -> object | None:
    """Refuse to start if another daemon is already running.

    Two daemons running simultaneously is the easiest way to get a "pastes
    twice" bug: both register the same hotkey, both fire, both paste. We
    use a named Windows mutex (process-scoped) so the lock is released
    automatically when this process exits, even if it crashes -- no stale
    pid file to clean up.

    The mutex is created in the Global\\ namespace so it spans logon
    sessions: a `pythonw run_daemon.py` zombie left over from an earlier
    session would otherwise be invisible to a fresh daemon started in a
    new session, and both would respond to the same hotkey. Creating
    Global\\ objects requires SeCreateGlobalPrivilege (held by admins
    and services); if that fails (non-elevated user) we fall back to
    Local\\, which still catches the common "two daemons in the same
    session" case.

    Returns the mutex handle (caller must keep it referenced for the
    lifetime of the process), or None on non-Windows / failure to lock.
    """
    if sys.platform != "win32":
        return None
    import ctypes
    ERROR_ALREADY_EXISTS = 183
    ERROR_ACCESS_DENIED = 5
    kernel32 = ctypes.windll.kernel32

    def _try(name: str) -> tuple[object | None, int]:
        h = kernel32.CreateMutexW(None, False, name)
        return h, kernel32.GetLastError()

    handle, err = _try("Global\\typing-assistant-daemon-singleton")
    if err == ERROR_ACCESS_DENIED or not handle:
        # Not elevated -- can't create Global objects. Fall back to Local.
        if handle:
            kernel32.CloseHandle(handle)
        log.warning(
            "singleton: Global\\ mutex denied (not elevated); falling back to "
            "Local\\. A daemon left over from a different logon session may go "
            "undetected. Run as admin for full protection."
        )
        handle, err = _try("Local\\typing-assistant-daemon-singleton")

    if err == ERROR_ALREADY_EXISTS:
        msg = (
            "ANOTHER DAEMON IS ALREADY RUNNING. Two daemons make every hotkey "
            "fire twice (=> 'pastes twice'). Close the other one and retry.\n"
            "Find it with: powershell \"Get-CimInstance Win32_Process -Filter "
            "\\\"Name='python.exe' OR Name='pythonw.exe'\\\" | Select ProcessId,Name,CommandLine\""
        )
        print(f"[typing-assistant] {msg}")
        log.error(msg)
        if handle:
            kernel32.CloseHandle(handle)
        sys.exit(2)
    return handle


def _send_ctrl_v_native() -> None:
    """Send Ctrl+V via Win32 SendInput, bypassing the `keyboard` library.

    Uses scan codes 0x1D (LCtrl) and 0x2F (V), with KEYEVENTF_SCANCODE so the
    OS doesn't remap based on the active layout. This is what fixes the bug
    where `keyboard.send('ctrl+v')` can resolve 'v' through the active layout
    and produce duplicate or wrong-key paste events on non-English layouts.
    """
    import ctypes
    from ctypes import wintypes

    KEYEVENTF_KEYUP = 0x0002
    KEYEVENTF_SCANCODE = 0x0008
    INPUT_KEYBOARD = 1

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", wintypes.WORD),
            ("wScan", wintypes.WORD),
            ("dwFlags", wintypes.DWORD),
            ("time", wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    # The OS expects sizeof(INPUT) to match the real struct, where the union
    # is sized to fit the LARGEST member (MOUSEINPUT, 32 bytes on x64). Without
    # padding the union to that size, SendInput rejects with ERROR_INVALID_PARAMETER.
    class _INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("ki", KEYBDINPUT),
            ("_pad", ctypes.c_byte * 32),
        ]

    class INPUT(ctypes.Structure):
        _anonymous_ = ("u",)
        _fields_ = [
            ("type", wintypes.DWORD),
            ("u", _INPUT_UNION),
        ]

    def _ev(scan: int, key_up: bool) -> INPUT:
        flags = KEYEVENTF_SCANCODE | (KEYEVENTF_KEYUP if key_up else 0)
        return INPUT(
            type=INPUT_KEYBOARD,
            u=_INPUT_UNION(ki=KEYBDINPUT(0, scan, flags, 0, None)),
        )

    LCTRL = 0x1D
    V = 0x2F
    seq = (INPUT * 4)(
        _ev(LCTRL, key_up=False),
        _ev(V, key_up=False),
        _ev(V, key_up=True),
        _ev(LCTRL, key_up=True),
    )
    sent = ctypes.windll.user32.SendInput(4, ctypes.byref(seq), ctypes.sizeof(INPUT))
    if sent != 4:
        log.warning(f"SendInput returned {sent}/4 (GetLastError={ctypes.windll.kernel32.GetLastError()})")


def _install_key_tracer() -> None:
    """Log every raw keyboard event the OS sees. Opt-in via TYPING_ASSISTANT_TRACE=1.

    WARNING: this logs every keystroke including passwords. Only enable while
    actively diagnosing a bug, then disable.
    """
    def _on_event(event) -> None:  # type: ignore[no-untyped-def]
        try:
            log.debug(
                f"KEY {event.event_type:<4} name={event.name!r} sc={event.scan_code} t={event.time:.3f}"
            )
        except Exception:
            pass

    kb.hook(_on_event)


def _release_modifiers() -> None:
    """Force shift/ctrl/alt up. Used both before sending ctrl+c (so a held
    Shift from the hotkey doesn't turn ctrl+c into shift+ctrl+c) and in the
    finally block (so an interrupted kb.send doesn't leave a modifier stuck)."""
    for mod in ('shift', 'ctrl', 'alt'):
        try:
            kb.release(mod)
        except Exception as e:
            log.debug(f"release({mod}) failed: {e}")


def _get_selected_text(call_id: str) -> str:
    """Copy selected text to clipboard and return it.

    Uses a sentinel value to distinguish "nothing was selected" (clipboard
    unchanged after ctrl+c) from "got real text". Without this, a flaky
    pyperclip.copy can leave the previous clipboard content in place and
    we'd treat it as the user's selection and paste it back -- the
    "pasted with no selection" bug.
    """
    try:
        old_clipboard = pyperclip.paste()
    except Exception as e:
        log.warning(f"[{call_id}] read old clipboard failed: {e}")
        old_clipboard = ""
    log.debug(f"[{call_id}] old clipboard: {len(old_clipboard)} chars")

    sentinel = f"\x00TA-SENTINEL-{uuid.uuid4().hex}\x00"
    try:
        pyperclip.copy(sentinel)
    except Exception as e:
        log.warning(f"[{call_id}] write sentinel failed: {e}")
        # If we can't even write a sentinel we cannot reliably detect
        # "no selection", so refuse to proceed.
        return ""
    time.sleep(0.05)

    _release_modifiers()
    time.sleep(0.05)

    log.debug(f"[{call_id}] sending ctrl+c")
    try:
        kb.send('ctrl+c')
    except Exception as e:
        log.warning(f"[{call_id}] kb.send(ctrl+c) failed: {e}")
    time.sleep(0.2)

    try:
        text = pyperclip.paste()
    except Exception as e:
        log.warning(f"[{call_id}] read clipboard after ctrl+c failed: {e}")
        text = ""

    if text == sentinel:
        log.info(f"[{call_id}] no selection (sentinel unchanged)")
        try:
            pyperclip.copy(old_clipboard)
        except Exception as e:
            log.debug(f"[{call_id}] restore clipboard failed: {e}")
        return ""

    if not text:
        log.info(f"[{call_id}] clipboard empty after ctrl+c")
        try:
            pyperclip.copy(old_clipboard)
        except Exception as e:
            log.debug(f"[{call_id}] restore clipboard failed: {e}")
        return ""

    log.debug(f"[{call_id}] copied {len(text)} chars")
    return text


def _paste_text(text: str, call_id: str) -> None:
    """Write text to clipboard and paste it."""
    try:
        pyperclip.copy(text)
    except Exception as e:
        log.warning(f"[{call_id}] write paste clipboard failed: {e}")
        return
    time.sleep(0.05)
    # Release modifiers again before paste: if the user is still physically
    # holding Shift from the hotkey, the app will see Shift+Ctrl+V (paste
    # special) instead of Ctrl+V, which can produce duplicated/odd pastes.
    _release_modifiers()
    time.sleep(0.02)
    if _USE_NATIVE_PASTE:
        log.debug(f"[{call_id}] sending ctrl+v via SendInput ({len(text)} chars)")
        try:
            _send_ctrl_v_native()
        except Exception as e:
            log.warning(f"[{call_id}] _send_ctrl_v_native failed: {e}")
    else:
        log.debug(f"[{call_id}] sending ctrl+v via kb.send ({len(text)} chars)")
        try:
            kb.send('ctrl+v')
        except Exception as e:
            log.warning(f"[{call_id}] kb.send(ctrl+v) failed: {e}")
    time.sleep(0.05)


def _run_processor(processor_fn: Callable[[str], str], tool_name: str) -> None:
    """Get selected text, run processor, paste result back."""
    global _last_call_at, _processing

    call_id = uuid.uuid4().hex[:6]
    log.debug(f"[{call_id}] hotkey fired: {tool_name}")

    with _processing_lock:
        if _processing:
            log.info(f"[{call_id}] dropped: already processing")
            return
        since = time.time() - _last_call_at
        if since < _RATE_LIMIT_S:
            log.info(f"[{call_id}] dropped: rate-limited ({since:.2f}s < {_RATE_LIMIT_S}s)")
            return
        _processing = True
        _last_call_at = time.time()

    log.info(f"[{call_id}] start: {tool_name}")
    try:
        text = _get_selected_text(call_id)
        if not text or not text.strip():
            log.info(f"[{call_id}] {tool_name}: no text -> abort (no paste)")
            return

        if len(text.strip()) < 2:
            log.info(f"[{call_id}] {tool_name}: text too short -> abort")
            return

        if not OPENAI_API_KEY and tool_name != "layout":
            log.info(f"[{call_id}] {tool_name}: no API key -> abort")
            return

        log.info(f"[{call_id}] input:  {text.strip()[:80]!r}")

        result = processor_fn(text.strip())

        log.info(f"[{call_id}] output: {result[:80]!r}")

        if result and result != text.strip():
            _paste_text(result, call_id)
            log.info(f"[{call_id}] {tool_name} applied")
        else:
            log.info(f"[{call_id}] {tool_name}: no change -> no paste")
    except Exception as e:
        log.exception(f"[{call_id}] {tool_name} error: {e}")
    finally:
        # Defensive: if kb.send was interrupted mid-sequence (exception, clipboard
        # block, etc.) a modifier can be left logically "down" in the OS, which
        # makes every subsequent keypress act like Ctrl/Shift+key until restart.
        _release_modifiers()
        with _processing_lock:
            _processing = False
        log.debug(f"[{call_id}] done")


def run_daemon() -> None:
    """Register hotkeys and block forever."""
    # Refuse to start if another daemon is already running. Keep `_singleton`
    # referenced for the process lifetime so the OS doesn't release the mutex.
    _singleton = _acquire_singleton()  # noqa: F841

    def on_layout() -> None:
        threading.Thread(target=_run_processor, args=(convert_auto, "layout"), daemon=True).start()

    def on_typo() -> None:
        threading.Thread(target=_run_processor, args=(correct_typos, "typo fix"), daemon=True).start()

    def on_rewrite() -> None:
        threading.Thread(target=_run_processor, args=(TOOLS["rewrite"], "rewrite"), daemon=True).start()

    def on_summarize() -> None:
        threading.Thread(target=_run_processor, args=(TOOLS["summarize"], "summarize"), daemon=True).start()

    def on_prompt_optimize() -> None:
        threading.Thread(target=_run_processor, args=(TOOLS["optimize_prompt"], "optimize prompt"), daemon=True).start()

    def on_expand_prompt() -> None:
        threading.Thread(target=_run_processor, args=(TOOLS["expand_prompt"], "expand prompt"), daemon=True).start()

    def on_humanize() -> None:
        threading.Thread(target=_run_processor, args=(TOOLS["humanize"], "humanize"), daemon=True).start()

    register_hotkeys(
        on_layout,
        on_typo,
        on_rewrite,
        on_summarize,
        on_prompt_optimize,
        on_expand_prompt,
        on_humanize,
    )

    if os.environ.get("TYPING_ASSISTANT_TRACE") == "1":
        _install_key_tracer()
        log.info("key tracer ENABLED (TYPING_ASSISTANT_TRACE=1)")

    if _USE_NATIVE_PASTE:
        log.info("native paste ENABLED (TYPING_ASSISTANT_NATIVE_PASTE=1)")

    print("[typing-assistant] daemon running")
    print("[typing-assistant] select text -> press hotkey -> text gets replaced")
    lp = log_path()
    if lp:
        print(f"[typing-assistant] log file: {lp}")
    else:
        print("[typing-assistant] log file: (disabled — could not open)")
    print()
    print("  Shift+F1 = fix keyboard layout")
    print("  Shift+F2 = fix typos")
    print("  Shift+F3 = rewrite professional")
    print("  Shift+F4 = summarize")
    print("  Shift+F5 = optimize prompt")
    print("  Shift+F6 = expand prompt")
    print("  Shift+F7 = humanize AI text")
    print()

    log.info("daemon started")
    kb.wait()
