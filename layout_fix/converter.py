"""Character conversion between Hebrew and English keyboard layouts."""

# Hebrew key → English key (physical key position on QWERTY)
HEBREW_TO_ENGLISH: dict[str, str] = {
    "ש": "a",
    "נ": "b",
    "ב": "c",
    "ג": "d",
    "ק": "e",
    "כ": "f",
    "ע": "g",
    "י": "h",
    "ן": "i",
    "ח": "j",
    "ל": "k",
    "ך": "l",
    "צ": "m",
    "מ": "n",
    "ם": "o",
    "פ": "p",
    "/": "q",
    "ר": "r",
    "ד": "s",
    "א": "t",
    "ט": "u",
    "ו": "v",
    "ה": "w",
    "ז": "x",
    "ס": "y",
    "ת": "z",
}

# English key → Hebrew key (reverse mapping)
ENGLISH_TO_HEBREW: dict[str, str] = {v: k for k, v in HEBREW_TO_ENGLISH.items()}


def convert_hebrew_to_english(text: str) -> str:
    """Convert text typed with Hebrew layout to English layout.

    Each Hebrew character is replaced by the English character
    on the same physical key. Non-mapped characters are left unchanged.

    Args:
        text: Input string (typically containing Hebrew letters).

    Returns:
        String with Hebrew characters replaced by English equivalents.
    """
    return "".join(HEBREW_TO_ENGLISH.get(c, c) for c in text)


def convert_english_to_hebrew(text: str) -> str:
    """Convert text typed with English layout to Hebrew layout.

    Each English letter (and /) is replaced by the Hebrew character
    on the same physical key. Non-mapped characters are left unchanged.

    Args:
        text: Input string (typically containing English letters).

    Returns:
        String with English characters replaced by Hebrew equivalents.
    """
    return "".join(ENGLISH_TO_HEBREW.get(c.lower(), c) for c in text)


def convert_auto(text: str) -> str:
    """Convert text in the direction suggested by layout detection.

    If the text is detected as mostly Hebrew, converts Hebrew → English.
    If mostly English, converts English → Hebrew.

    Args:
        text: Input string in either layout.

    Returns:
        Converted string.
    """
    from layout_fix.detector import detect_layout

    layout = detect_layout(text)
    if layout == "hebrew":
        return convert_hebrew_to_english(text)
    return convert_english_to_hebrew(text)
