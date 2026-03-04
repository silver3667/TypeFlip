"""Main daemon: keyboard listener, buffer, and hotkey-triggered fix flow."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable

from pynput import keyboard

from config.settings import DEBUG, OPENAI_API_KEY
from daemon.key_buffer import KeyBuffer
from daemon.hotkeys import register_hotkeys
from processors.layout_converter import convert_auto
from processors.typo_corrector import correct_typos
from tools.registry import TOOLS

# Rate limit: ignore AI calls within 0.5s of the last one
_last_ai_call = 0.0

# When True, key events from our own controller.type() are ignored (no double buffer push).
_injecting = False
_injecting_lock = threading.Lock()


def _set_injecting(value: bool) -> None:
    with _injecting_lock:
        global _injecting
        _injecting = value


def _is_injecting() -> bool:
    with _injecting_lock:
        return _injecting


def _run_fix_flow(
    buffer: KeyBuffer,
    controller: keyboard.Controller,
    do_layout: bool,
    do_typo: bool,
) -> None:
    """Read buffer, optionally convert layout, optionally correct typos, backspace, type result."""
    global _last_ai_call
    segment, length_to_delete = buffer.get_last_segment()
    if not segment:
        return
    if do_typo:
        if not OPENAI_API_KEY:
            return  # Skip AI if no API key
        if time.time() - _last_ai_call < 0.5:
            return
        if len(segment) < 6:
            return
        _last_ai_call = time.time()
    text = segment
    if do_layout:
        text = convert_auto(text)
    if do_typo:
        text = correct_typos(text)
    # Update buffer: remove the segment we're replacing
    buffer.consume(length_to_delete)
    # Send backspaces
    for _ in range(length_to_delete):
        controller.press(keyboard.Key.backspace)
        controller.release(keyboard.Key.backspace)
    # Type corrected text (don't record our own typing in buffer)
    _set_injecting(True)
    try:
        controller.type(text)
    finally:
        _set_injecting(False)
    # Keep buffer in sync: we just typed `text`
    for c in text:
        buffer.push(c)
    if do_layout and not do_typo:
        print("[typing-assistant] layout fix applied")
    elif do_typo and not do_layout:
        print("[typing-assistant] typo fix applied")
    elif do_layout and do_typo:
        print("[typing-assistant] layout + typo applied")


def _run_prompt_optimize_flow(
    buffer: KeyBuffer,
    controller: keyboard.Controller,
) -> None:
    """Read last sentence from buffer, optimize as AI prompt, backspace, type result. No clipboard."""
    global _last_ai_call
    buffer_text, length_to_delete = buffer.read_last_sentence()
    if not buffer_text:
        return
    if len(buffer_text) < 6:
        return
    if not OPENAI_API_KEY:
        return
    if time.time() - _last_ai_call < 0.5:
        return
    _last_ai_call = time.time()
    if DEBUG:
        print(f"[typing-assistant] processor=optimize_prompt")
        print(f"input={buffer_text}")
    optimized = TOOLS["optimize_prompt"](buffer_text)
    if DEBUG:
        print(f"output={optimized}")
    if optimized == buffer_text:
        return
    buffer.consume(length_to_delete)
    for _ in range(length_to_delete):
        controller.press(keyboard.Key.backspace)
        controller.release(keyboard.Key.backspace)
    _set_injecting(True)
    try:
        controller.type(optimized)
    finally:
        _set_injecting(False)
    for c in optimized:
        buffer.push(c)
    print("[typing-assistant] optimize prompt applied")


def _run_sentence_processor_flow(
    buffer: KeyBuffer,
    controller: keyboard.Controller,
    processor_fn: Callable[[str], str],
    tool_name: str,
) -> None:
    """Read last sentence from buffer, run processor, backspace, type result if different. No clipboard."""
    global _last_ai_call
    buffer_text, length_to_delete = buffer.read_last_sentence()
    if not buffer_text:
        return
    if len(buffer_text) < 6:
        return
    if not OPENAI_API_KEY:
        return
    if time.time() - _last_ai_call < 0.5:
        return
    _last_ai_call = time.time()
    if DEBUG:
        print(f"[typing-assistant] processor={processor_fn.__name__}")
        print(f"input={buffer_text}")
    result = processor_fn(buffer_text)
    if DEBUG:
        print(f"output={result}")
    if result == buffer_text:
        return
    buffer.consume(length_to_delete)
    for _ in range(length_to_delete):
        controller.press(keyboard.Key.backspace)
        controller.release(keyboard.Key.backspace)
    _set_injecting(True)
    try:
        controller.type(result)
    finally:
        _set_injecting(False)
    for c in result:
        buffer.push(c)
    print(f"[typing-assistant] {tool_name} applied")


def run_daemon() -> None:
    """Start keyboard listener and hotkeys; block until stopped."""
    buffer = KeyBuffer()
    controller = keyboard.Controller()

    def on_layout() -> None:
        _run_fix_flow(buffer, controller, do_layout=True, do_typo=False)

    def on_typo() -> None:
        _run_fix_flow(buffer, controller, do_layout=False, do_typo=True)

    def on_layout_then_typo() -> None:
        _run_fix_flow(buffer, controller, do_layout=True, do_typo=True)

    def on_prompt_optimize() -> None:
        _run_prompt_optimize_flow(buffer, controller)

    def on_rewrite() -> None:
        _run_sentence_processor_flow(buffer, controller, TOOLS["rewrite"], "rewrite")

    def on_summarize() -> None:
        _run_sentence_processor_flow(buffer, controller, TOOLS["summarize"], "summarize")

    def on_expand_prompt() -> None:
        _run_sentence_processor_flow(buffer, controller, TOOLS["expand_prompt"], "expand prompt")

    def on_quick_fix() -> None:
        _run_sentence_processor_flow(buffer, controller, TOOLS["quick_fix"], "quick fix")

    def on_press(key: keyboard.Key | keyboard.KeyCode | None) -> None:
        if _is_injecting():
            return
        try:
            if hasattr(key, "char") and key.char is not None:
                buffer.push(key.char)
            elif key == keyboard.Key.backspace:
                buffer.consume(1)
        except Exception:
            pass

    hotkeys = register_hotkeys(
        on_layout,
        on_typo,
        on_layout_then_typo,
        on_prompt_optimize,
        on_rewrite,
        on_summarize,
        on_expand_prompt,
        on_quick_fix,
    )
    with keyboard.Listener(on_press=on_press), hotkeys:
        hotkeys.join()
