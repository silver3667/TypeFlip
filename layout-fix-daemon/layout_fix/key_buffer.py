"""
Rolling buffer that stores the last N characters typed.
"""

from collections import deque
from threading import Lock


class KeyBuffer:
    """Thread-safe rolling buffer of recently typed characters."""

    def __init__(self, max_size: int = 200):
        self._max_size = max_size
        self._buffer: deque[str] = deque(maxlen=max_size)
        self._lock = Lock()

    def push(self, char: str) -> None:
        """Add a character to the buffer (drops oldest if full)."""
        if not char:
            return
        with self._lock:
            self._buffer.append(char)

    def push_backspace(self) -> None:
        """Remove the last character (simulate backspace in buffer)."""
        with self._lock:
            if self._buffer:
                self._buffer.pop()

    def read_and_clear(self) -> str:
        """Read current buffer content and clear it. Returns the text."""
        with self._lock:
            text = "".join(self._buffer)
            self._buffer.clear()
            return text

    def read(self) -> str:
        """Read current buffer content without clearing."""
        with self._lock:
            return "".join(self._buffer)

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._buffer.clear()

    def length(self) -> int:
        """Current number of characters in buffer."""
        with self._lock:
            return len(self._buffer)
