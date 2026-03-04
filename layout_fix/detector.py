"""Detect whether text is mostly in Hebrew or English keyboard layout."""

# Unicode range for Hebrew letters (including punctuation and marks)
HEBREW_FIRST = "\u0590"
HEBREW_LAST = "\u05FF"


def _is_hebrew_char(c: str) -> bool:
    """Return True if the character is in the Hebrew Unicode block."""
    return len(c) == 1 and HEBREW_FIRST <= c <= HEBREW_LAST


def _is_english_letter(c: str) -> bool:
    """Return True if the character is an ASCII letter (a-z, A-Z)."""
    return len(c) == 1 and c.isascii() and c.isalpha()


def detect_layout(text: str) -> str:
    """Detect whether text is mostly Hebrew or English.

    Counts Hebrew characters (Unicode U+0590–U+05FF) and English letters
    (ASCII a-z, A-Z). The majority decides the layout. If neither dominates
    or text is empty, defaults to "english".

    Args:
        text: Input string to analyze.

    Returns:
        "hebrew" if mostly Hebrew characters, otherwise "english".
    """
    if not text.strip():
        return "english"

    hebrew_count = sum(1 for c in text if _is_hebrew_char(c))
    english_count = sum(1 for c in text if _is_english_letter(c))

    if hebrew_count > english_count:
        return "hebrew"
    return "english"
