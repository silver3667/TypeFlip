"""
Hotkey registration and handling.
Uses 'keyboard' for global hotkey (CTRL+;) and 'pynput' for key recording.
"""

import threading
from typing import Callable

import keyboard as kb


def register_hotkey(combination: str, callback: Callable[[], None]) -> None:
    """Register a global hotkey. combination e.g. 'ctrl+;'."""
    kb.add_hotkey(combination, callback)


def unregister_hotkey(combination: str) -> None:
    """Remove hotkey."""
    kb.remove_hotkey(combination)


def trigger_backspaces(count: int) -> None:
    """Send 'count' backspace key presses (no clipboard)."""
    for _ in range(count):
        kb.send("backspace")


def type_text(text: str) -> None:
    """Type text character by character (no clipboard)."""
    kb.write(text)
