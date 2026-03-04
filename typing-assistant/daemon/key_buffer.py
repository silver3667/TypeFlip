"""Rolling keyboard buffer: stores recent keystrokes and exposes last sentence/token."""

import re

from config.settings import MAX_BUFFER_SIZE


class KeyBuffer:
    """Rolling buffer of typed characters. Drops oldest when over MAX_BUFFER_SIZE."""

    def __init__(self, max_size: int | None = None) -> None:
        self._max_size = max_size if max_size is not None else MAX_BUFFER_SIZE
        self._chars: list[str] = []

    def push(self, char: str) -> None:
        """Append one character; drop from the left if over max size."""
        if len(char) != 1:
            return
        self._chars.append(char)
        while len(self._chars) > self._max_size:
            self._chars.pop(0)

    def clear(self) -> None:
        """Remove all characters."""
        self._chars.clear()

    def get_all(self) -> str:
        """Return full buffer content."""
        return "".join(self._chars)

    def read_last_sentence(self) -> tuple[str, int]:
        """
        Return the last sentence (or last token) and the number of chars to delete.
        Same as get_last_segment(); use for prompt optimization and similar flows.
        """
        return self.get_last_segment()

    def get_last_segment(self) -> tuple[str, int]:
        """
        Return the last sentence or last token to process, and how many chars to delete.
        - Prefer last sentence (text after last ., !, ?, newline).
        - Otherwise last token (run of word chars / run of non-space).
        - If buffer is small or no boundary, return full buffer.
        Returns (segment_text, length_to_delete_from_buffer_end).
        """
        text = self.get_all()
        if not text:
            return "", 0
        trimmed = text.rstrip()
        if not trimmed:
            return "", len(self._chars)

        # Last sentence: from last sentence terminator or newline
        for sep in (". ", "! ", "? ", ".\n", "!\n", "?\n", "\n"):
            idx = trimmed.rfind(sep)
            if idx != -1:
                segment = trimmed[idx + len(sep) :].strip()
                if segment:
                    start = trimmed.rfind(segment)
                    if start != -1:
                        length_to_delete = len(text) - start
                        return segment, length_to_delete
        # Last token: last run of word chars or last run of non-space
        match = re.search(r"(?:[^\s]+|\S+)\s*$", trimmed)
        if match:
            segment = match.group(0).strip()
            if segment:
                start = trimmed.rfind(segment)
                if start != -1:
                    length_to_delete = len(text) - start
                    return segment, length_to_delete
        return trimmed, len(self._chars)

    def consume(self, count: int) -> None:
        """Remove the last `count` characters from the buffer (after we backspaced them)."""
        if count <= 0:
            return
        for _ in range(min(count, len(self._chars))):
            if self._chars:
                self._chars.pop()
