"""Typo and grammar correction using AI."""

from ai.openai_client import correct_text as _correct_text


def correct_typos(text: str) -> str:
    """Fix spelling and grammar in text. Returns only the corrected sentence."""
    return _correct_text(text)
