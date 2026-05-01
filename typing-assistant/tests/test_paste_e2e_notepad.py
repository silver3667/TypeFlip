"""End-to-end test using Notepad as a real Win32 edit control.

The Tk-based test in test_paste_e2e.py runs into a Tk peculiarity: Tk binds
paste to keysym 'v', so when Hebrew layout is active and V maps to a Hebrew
keysym, Tk doesn't trigger paste at all. Real Windows apps handle Ctrl+V via
virtual-key in WndProc, independent of layout, so they'd still paste.

This test launches Notepad, types known text, paste-replaces it via the
daemon's _paste_text, then reads the field via clipboard, and checks for the
"pastes twice" bug under both English and Hebrew layouts, with both the
keyboard library and native SendInput paste paths.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import sys
import time
from ctypes import wintypes

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    sys.stderr.reconfigure(encoding="utf-8", errors="backslashreplace")
except Exception:
    pass

import keyboard as kb
import pyperclip

from daemon.daemon import _send_ctrl_v_native

HEBREW_HKL = 0x040D
ENGLISH_HKL = 0x0409
WM_INPUTLANGCHANGEREQUEST = 0x0050
INPUTLANGCHANGE_FORWARD = 0x0002
WM_CLOSE = 0x0010

user32 = ctypes.windll.user32


def _activate_layout(lang_id: int) -> None:
    hwnd = user32.GetForegroundWindow()
    hkl_str = f"{lang_id:08X}"
    hkl = user32.LoadKeyboardLayoutW(hkl_str, 1)
    user32.PostMessageW(hwnd, WM_INPUTLANGCHANGEREQUEST, INPUTLANGCHANGE_FORWARD, hkl)
    time.sleep(0.25)


def _current_lang() -> int:
    return user32.GetKeyboardLayout(0) & 0xFFFF


def _bring_to_front(hwnd: int) -> None:
    kb.press_and_release("alt")
    time.sleep(0.05)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.25)


def _find_notepad_edit(np_hwnd: int) -> int:
    """Walk children to find the actual edit control. On Win11 Notepad uses
    'RichEditD2DPT'; on classic notepad it's 'Edit'."""
    candidates = ["Edit", "RichEditD2DPT", "RICHEDIT50W"]

    found = ctypes.c_void_p(0)

    @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    def enum_proc(hwnd, lparam):
        cls = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(hwnd, cls, 64)
        if cls.value in candidates:
            found.value = hwnd
            return False  # stop
        return True

    user32.EnumChildWindows(np_hwnd, enum_proc, 0)
    return found.value or 0


def _wait_for_notepad() -> tuple[subprocess.Popen, int, int]:
    proc = subprocess.Popen(["notepad.exe"])
    deadline = time.time() + 8.0
    while time.time() < deadline:
        time.sleep(0.2)
        hwnd = user32.FindWindowW("Notepad", None)
        if not hwnd:
            # Win11 Notepad uses a different class name.
            hwnd = user32.FindWindowExW(0, 0, "ApplicationFrameWindow", None)
        if hwnd:
            edit = _find_notepad_edit(hwnd)
            # If we can't find edit immediately, retry — UI hierarchy may
            # still be initializing.
            if edit:
                return proc, hwnd, edit
            # Even without finding edit class, the main hwnd is enough since
            # SendInput delivers to whatever has keyboard focus.
            return proc, hwnd, 0
    raise RuntimeError("could not find Notepad window")


def _kill(proc: subprocess.Popen, hwnd: int) -> None:
    try:
        user32.PostMessageW(hwnd, WM_CLOSE, 0, 0)
    except Exception:
        pass
    time.sleep(0.3)
    if proc.poll() is None:
        try:
            proc.kill()
        except Exception:
            pass


def _read_field_via_clipboard() -> str:
    """Select-all + copy in the foreground edit, return clipboard."""
    pyperclip.copy("\x00SENTINEL\x00")
    time.sleep(0.1)
    kb.send("ctrl+a")
    time.sleep(0.1)
    kb.send("ctrl+c")
    time.sleep(0.2)
    return pyperclip.paste()


def _run_case(name: str, *, lang_id: int, use_native: bool, payload: str) -> tuple[bool, str]:
    proc, hwnd, _edit = _wait_for_notepad()
    try:
        _bring_to_front(hwnd)
        # Type the seed text using kb.write so we don't need an edit handle.
        # Notepad will receive it via the focused control.
        kb.write("ABC", delay=0.01)
        time.sleep(0.2)
        kb.send("ctrl+a")
        time.sleep(0.15)

        _activate_layout(lang_id)
        if _current_lang() != lang_id:
            return False, f"<layout switch failed: 0x{_current_lang():04X}>"

        pyperclip.copy(payload)
        time.sleep(0.1)
        if use_native:
            _send_ctrl_v_native()
        else:
            kb.send("ctrl+v")
        time.sleep(0.4)

        # Switch back so ctrl+a/ctrl+c work consistently.
        _activate_layout(ENGLISH_HKL)
        time.sleep(0.2)

        observed = _read_field_via_clipboard()
        return observed == payload, observed
    finally:
        try:
            _activate_layout(ENGLISH_HKL)
        except Exception:
            pass
        _kill(proc, hwnd)


def main() -> int:
    """Tests the raw paste mechanism. If any of these output the payload twice
    (DOUBLE marker), the bug is in our paste path. If all are OK, the paste
    mechanism is fine and the user's "pastes twice" bug is environmental
    (most likely two daemon instances running -- see test_singleton.py)."""
    paste_cases = [
        ("kbsend-english", ENGLISH_HKL, False, "REPLACED-EN"),
        ("kbsend-hebrew", HEBREW_HKL, False, "REPLACED-HE"),
        ("native-english", ENGLISH_HKL, True, "REPLACED-NAT-EN"),
        ("native-hebrew", HEBREW_HKL, True, "REPLACED-NAT-HE"),
    ]
    results = []

    print("--- raw paste tests ---")
    for name, lang, native, payload in paste_cases:
        try:
            passed, observed = _run_case(name, lang_id=lang, use_native=native, payload=payload)
        except Exception as e:
            passed, observed = False, f"<exception: {e}>"
        is_double = observed == payload + payload
        marker = "DOUBLE" if is_double else ("OK " if passed else "FAIL")
        print(f"[{marker:6s}] {name:20s} expected={payload!r:25s} observed={observed!r}")
        results.append((name, passed))

    failures = [r for r in results if not r[1]]
    if failures:
        print(f"\n{len(failures)}/{len(results)} cases failed")
        return 1
    print(f"\nall {len(results)} cases passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
