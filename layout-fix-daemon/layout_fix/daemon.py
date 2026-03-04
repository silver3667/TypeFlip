"""
Background daemon: records keystrokes and on hotkey fixes layout.
Does NOT use clipboard.
"""

import threading
from pynput import keyboard as pynput_kb

from layout_fix.converter import convert_auto
from layout_fix.key_buffer import KeyBuffer
from layout_fix.hotkeys import register_hotkey, trigger_backspaces, type_text


# Default hotkey: Ctrl+;
DEFAULT_HOTKEY = "ctrl+;"

# Buffer size
BUFFER_SIZE = 200


def _on_press_callback(key_buffer: KeyBuffer):
    """Build callback that pushes key to buffer on key press."""

    def _on_press(key):
        try:
            if hasattr(key, "char") and key.char is not None:
                key_buffer.push(key.char)
            elif key == pynput_kb.Key.backspace:
                key_buffer.push_backspace()
        except Exception:
            pass

    return _on_press


def _on_hotkey(key_buffer: KeyBuffer) -> None:
    """On Ctrl+;: read buffer, convert, delete original, type corrected."""
    text = key_buffer.read_and_clear()
    if not text:
        return
    converted = convert_auto(text)
    if converted == text:
        # No change or empty; restore buffer so user doesn't lose text
        for c in text:
            key_buffer.push(c)
        return
    # Delete the original characters (backspace N times)
    trigger_backspaces(len(text))
    # Type the corrected text
    type_text(converted)


def run_daemon(
    hotkey: str = DEFAULT_HOTKEY,
    buffer_size: int = BUFFER_SIZE,
) -> None:
    """
    Run the layout-fix daemon. Blocks until stopped.
    - Listens to keyboard and fills a rolling buffer.
    - On hotkey: convert buffer, backspace, type result.
    """
    key_buffer = KeyBuffer(max_size=buffer_size)

    # Register hotkey first
    register_hotkey(hotkey, lambda: _on_hotkey(key_buffer))

    # Start pynput listener in a daemon thread so main thread can block/wait
    listener = pynput_kb.Listener(on_press=_on_press_callback(key_buffer))
    listener.daemon = True
    listener.start()

    try:
        # Keep running until KeyboardInterrupt
        while True:
            listener.join(timeout=1.0)
            if not listener.is_alive():
                break
    except KeyboardInterrupt:
        pass
    finally:
        listener.stop()
