"""Quick fix: layout conversion + typo correction (no additional AI)."""

from processors.layout_converter import convert_auto
from processors.typo_corrector import correct_typos


def quick_fix(text: str) -> str:
    """Convert keyboard layout, then correct typos. Returns corrected text."""
    text = convert_auto(text)
    return correct_typos(text)
