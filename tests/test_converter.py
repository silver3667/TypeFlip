"""Tests for layout conversion and detection."""

import pytest

from layout_fix.converter import (
    convert_auto,
    convert_english_to_hebrew,
    convert_hebrew_to_english,
)
from layout_fix.detector import detect_layout


# "how are things" in Hebrew key positions (י→h, ם→o, ה→w, ש→a, ר→r, ק→e, א→t, י→h, ן→i, מ→n, ע→g, ד→s)
HEBREW_HOW_ARE_THINGS = "\u05D9\u05DD\u05D4 \u05E9\u05E8\u05E7 \u05D0\u05D9\u05DF\u05DE\u05E2\u05D3"  # ימה שרק איינמד


def test_hebrew_to_english() -> None:
    """Typed-in-Hebrew text converts to correct English."""
    result = convert_hebrew_to_english(HEBREW_HOW_ARE_THINGS)
    assert result == "how are things"


def test_english_to_hebrew() -> None:
    """English text converts to correct Hebrew layout equivalents."""
    result = convert_english_to_hebrew("how are things")
    assert result == HEBREW_HOW_ARE_THINGS


def test_hebrew_to_english_identity_roundtrip() -> None:
    """Hebrew→English→Hebrew roundtrip preserves content."""
    to_english = convert_hebrew_to_english(HEBREW_HOW_ARE_THINGS)
    back_to_hebrew = convert_english_to_hebrew(to_english)
    assert back_to_hebrew == HEBREW_HOW_ARE_THINGS


def test_english_to_hebrew_identity_roundtrip() -> None:
    """English→Hebrew→English roundtrip preserves content."""
    english = "hello world"
    to_hebrew = convert_english_to_hebrew(english)
    back_to_english = convert_hebrew_to_english(to_hebrew)
    assert back_to_english == english


def test_auto_detection() -> None:
    """convert_auto detects Hebrew and converts to English."""
    result = convert_auto(HEBREW_HOW_ARE_THINGS)
    assert result == "how are things"


def test_auto_detection_english_to_hebrew() -> None:
    """convert_auto detects English and converts to Hebrew."""
    result = convert_auto("how are things")
    assert result == HEBREW_HOW_ARE_THINGS


def test_detect_layout_hebrew() -> None:
    """Mostly Hebrew text is detected as hebrew."""
    assert detect_layout("שלום עולם") == "hebrew"
    assert detect_layout(HEBREW_HOW_ARE_THINGS) == "hebrew"


def test_detect_layout_english() -> None:
    """Mostly English text is detected as english."""
    assert detect_layout("how are things") == "english"
    assert detect_layout("hello") == "english"


def test_detect_layout_empty_defaults_english() -> None:
    """Empty or whitespace defaults to english."""
    assert detect_layout("") == "english"
    assert detect_layout("   ") == "english"


def test_converter_ignores_unknown_chars() -> None:
    """Characters not in the mapping are left unchanged."""
    mixed = "hello 123 world!"
    result = convert_english_to_hebrew(mixed)
    assert "123" in result
    assert "!" in result
