"""
Hebrew ↔ English keyboard layout conversion based on physical key positions.
Uses standard Israeli SI-1452 layout mapping. Do not change this mapping.
"""

# Physical key mapping: same key produces different character in each layout.
# English (QWERTY) -> Hebrew (SI-1452)
ENGLISH_TO_HEBREW = {
    "q": "/",
    "w": "'",
    "e": "ק",
    "r": "ר",
    "t": "א",
    "y": "ט",
    "u": "ו",
    "i": "ן",
    "o": "ם",
    "p": "פ",
    "a": "ש",
    "s": "ד",
    "d": "ג",
    "f": "כ",
    "g": "ע",
    "h": "י",
    "j": "ח",
    "k": "ל",
    "l": "ך",
    "z": "ז",
    "x": "ס",
    "c": "ב",
    "v": "ה",
    "b": "נ",
    "n": "מ",
    "m": "צ",
    ";": "׳",
    "'": "\\",
    ",": "ת",
    ".": "ץ",
    "/": ".",
    "[": "[",
    "]": "]",
    "`": "`",
    "-": "-",
    "=": "=",
    "\\": "\\",
    "Q": "/",
    "W": "'",
    "E": "ק",
    "R": "ר",
    "T": "א",
    "Y": "ט",
    "U": "ו",
    "I": "ן",
    "O": "ם",
    "P": "פ",
    "A": "ש",
    "S": "ד",
    "D": "ג",
    "F": "כ",
    "G": "ע",
    "H": "י",
    "J": "ח",
    "K": "ל",
    "L": "ך",
    "Z": "ז",
    "X": "ס",
    "C": "ב",
    "V": "ה",
    "B": "נ",
    "N": "מ",
    "M": "צ",
    ":": "׳",
    '"': "\\",
    "<": "ת",
    ">": "ץ",
    "?": ".",
}

# Hebrew -> English (reverse mapping); prefer lowercase English
HEBREW_TO_ENGLISH = {}
for k, v in ENGLISH_TO_HEBREW.items():
    if k.isalpha() and k.isupper():
        continue
    if v not in HEBREW_TO_ENGLISH:
        HEBREW_TO_ENGLISH[v] = k
HEBREW_TO_ENGLISH["׳"] = ";"

# Hebrew letters (Unicode range for Hebrew plus punctuation)
HEBREW_LETTERS = set(
    "אבגדהוזחטסעפצקרשת"
    "ךםןףץ"
    "׳"
)


def convert_hebrew_to_english(text: str) -> str:
    """Convert text from Hebrew keyboard layout to English (QWERTY)."""
    result = []
    for char in text:
        result.append(HEBREW_TO_ENGLISH.get(char, char))
    return "".join(result)


def convert_english_to_hebrew(text: str) -> str:
    """Convert text from English (QWERTY) keyboard layout to Hebrew."""
    result = []
    for char in text:
        result.append(ENGLISH_TO_HEBREW.get(char, char))
    return "".join(result)


def _hebrew_ratio(text: str) -> float:
    """Return ratio of Hebrew characters in text (0.0 to 1.0)."""
    if not text or not text.strip():
        return 0.0
    letters = [c for c in text if c.isalpha() or c in HEBREW_LETTERS or c in "׳"]
    if not letters:
        return 0.0
    hebrew_count = sum(1 for c in letters if c in HEBREW_LETTERS or c in "׳")
    return hebrew_count / len(letters)


def convert_auto(text: str) -> str:
    """
    Auto-detect layout and convert.
    - If text is mostly Hebrew -> convert to English.
    - If text is mostly English (or mixed) -> convert to Hebrew.
    """
    if not text or not text.strip():
        return text
    ratio = _hebrew_ratio(text)
    if ratio >= 0.5:
        return convert_hebrew_to_english(text)
    return convert_english_to_hebrew(text)
