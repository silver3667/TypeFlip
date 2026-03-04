"""Global hotkey registration and layout-fix action."""

import sys
import time
from collections.abc import Callable

import pyperclip

from layout_fix.converter import convert_auto

# Backend for key simulation: "keyboard" or "pynput". Set when registering hotkey.
_sender: str | None = None
_pynput_controller: object = None


def _send_select_all() -> None:
    """Send Ctrl+A to select all in the focused control."""
    if _sender == "pynput":
        from pynput.keyboard import Controller, Key

        c = Controller()
        with c.pressed(Key.ctrl):
            c.press("a")
            c.release("a")
    else:
        import keyboard

        keyboard.send("ctrl+a")


def _send_copy() -> None:
    """Send Ctrl+C to copy selection."""
    if _sender == "pynput":
        from pynput.keyboard import Controller, Key

        c = Controller()
        with c.pressed(Key.ctrl):
            c.press("c")
            c.release("c")
    else:
        import keyboard

        keyboard.send("ctrl+c")


def _send_paste() -> None:
    """Send Ctrl+V to paste."""
    if _sender == "pynput":
        from pynput.keyboard import Controller, Key

        c = Controller()
        with c.pressed(Key.ctrl):
            c.press("v")
            c.release("v")
    else:
        import keyboard

        keyboard.send("ctrl+v")


def fix_layout() -> None:
    """Copy focused text, detect layout, convert, and paste back.

    Simulates: Select All → Copy → convert clipboard → Paste.
    Uses short delays so the target app has time to respond.
    """
    time.sleep(0.05)
    _send_select_all()
    time.sleep(0.08)
    _send_copy()
    time.sleep(0.08)

    try:
        text = pyperclip.paste()
    except Exception:
        return

    if not text:
        return

    converted = convert_auto(text)
    if converted == text:
        return

    try:
        pyperclip.copy(converted)
    except Exception:
        return

    time.sleep(0.05)
    _send_paste()


def _register_keyboard(handler: Callable[[], None]) -> bool:
    """Use keyboard library; return True if successful."""
    global _sender
    try:
        import keyboard

        keyboard.add_hotkey("ctrl+alt+t", handler, suppress=False)
        _sender = "keyboard"
        return True
    except Exception as e:
        if "root" in str(e).lower() or "permission" in str(e).lower():
            return False
        raise


def _register_pynput(handler: Callable[[], None]) -> None:
    """Use pynput for hotkey and key sending (works without root on Linux)."""
    global _sender
    from pynput import keyboard as pynput_kb

    _sender = "pynput"

    def on_activate() -> None:
        handler()

    with pynput_kb.GlobalHotKeys({"<ctrl>+<alt>+t": on_activate}) as h:
        h.join()


def register_hotkey(handler: Callable[[], None] = fix_layout) -> None:
    """Register the global hotkey Ctrl+Alt+T to run the given handler.

    Tries the keyboard library first; on Linux without root, falls back to pynput.
    """
    if _register_keyboard(handler):
        import keyboard

        keyboard.wait()
    else:
        if sys.platform == "linux":
            print("Note: Running without root — using pynput for hotkey (no sudo needed).")
        _register_pynput(handler)


def wait_forever() -> None:
    """Block until the process is terminated (e.g. Ctrl+C)."""
    # wait is called from inside register_hotkey (keyboard.wait or pynput join)
    pass
