"""Main daemon: clipboard-based hotkey processing.

Workflow: user selects text -> presses hotkey -> daemon copies selection,
processes it, and pastes the result back.
"""

from __future__ import annotations

import time
import threading
from collections.abc import Callable

import keyboard as kb
import pyperclip

from config.settings import DEBUG, OPENAI_API_KEY
from daemon.hotkeys import register_hotkeys
from processors.layout_converter import convert_auto
from processors.typo_corrector import correct_typos
from tools.registry import TOOLS

# Rate limit: ignore AI calls within 0.5s of the last one
_last_ai_call = 0.0
_processing = False
_processing_lock = threading.Lock()


def _get_selected_text() -> str:
    """Copy selected text to clipboard and return it."""
    try:
        old_clipboard = pyperclip.paste()
    except Exception:
        old_clipboard = ""

    pyperclip.copy("")
    time.sleep(0.05)
    kb.send('ctrl+c')
    time.sleep(0.15)

    try:
        text = pyperclip.paste()
    except Exception:
        text = ""

    if not text:
        try:
            pyperclip.copy(old_clipboard)
        except Exception:
            pass
        return ""

    return text


def _paste_text(text: str) -> None:
    """Write text to clipboard and paste it."""
    pyperclip.copy(text)
    time.sleep(0.05)
    kb.send('ctrl+v')
    time.sleep(0.05)


def _run_processor(processor_fn: Callable[[str], str], tool_name: str) -> None:
    """Get selected text, run processor, paste result back."""
    global _last_ai_call, _processing

    with _processing_lock:
        if _processing:
            return
        _processing = True

    try:
        text = _get_selected_text()
        if not text or not text.strip():
            if DEBUG:
                print(f"[typing-assistant] {tool_name}: no text selected")
            return

        if len(text.strip()) < 2:
            return

        if not OPENAI_API_KEY and tool_name != "layout":
            if DEBUG:
                print(f"[typing-assistant] {tool_name}: no API key")
            return

        if tool_name != "layout":
            if time.time() - _last_ai_call < 0.5:
                return
            _last_ai_call = time.time()

        if DEBUG:
            print(f"[typing-assistant] {tool_name}")
            print(f"  input:  {text.strip()[:80]}")

        result = processor_fn(text.strip())

        if DEBUG:
            print(f"  output: {result[:80]}")

        if result and result != text.strip():
            _paste_text(result)
            print(f"[typing-assistant] {tool_name} applied")
        else:
            if DEBUG:
                print(f"[typing-assistant] {tool_name}: no change")
    except Exception as e:
        print(f"[typing-assistant] {tool_name} error: {e}")
    finally:
        with _processing_lock:
            _processing = False


def run_daemon() -> None:
    """Register hotkeys and block forever."""

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

    print("[typing-assistant] daemon running")
    print("[typing-assistant] select text -> press hotkey -> text gets replaced")
    print()
    print("  Shift+F1 = fix keyboard layout")
    print("  Shift+F2 = fix typos")
    print("  Shift+F3 = rewrite professional")
    print("  Shift+F4 = summarize")
    print("  Shift+F5 = optimize prompt")
    print("  Shift+F6 = expand prompt")
    print("  Shift+F7 = humanize AI text")
    print()

    kb.wait()
