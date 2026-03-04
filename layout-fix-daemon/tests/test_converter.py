"""
Pytest tests for layout conversion: Hebrew ↔ English and auto-detection.
"""

import pytest

from layout_fix.converter import (
    convert_hebrew_to_english,
    convert_english_to_hebrew,
    convert_auto,
)


class TestHebrewToEnglish:
    """Hebrew → English conversion (by physical key position)."""

    def test_how_are_you(self):
        # "ים'" = keys for h, o, w in Hebrew layout (י=h, ם=o, '=w)
        assert convert_hebrew_to_english("ים'") == "how"

    def test_shalom(self):
        # ש=a, ל=k, ו=u, ם=o (physical key positions)
        assert convert_hebrew_to_english("שלום") == "akuo"

    def test_preserves_spaces_and_punctuation(self):
        assert convert_hebrew_to_english("ש  ד") == "a  s"
        # ע=g, ץ=. (same key as / in English)
        assert convert_hebrew_to_english("עץע") == "g.g"

    def test_unknown_chars_unchanged(self):
        assert convert_hebrew_to_english("123") == "123"
        assert convert_hebrew_to_english("ש123ד") == "a123s"

    def test_geresh(self):
        assert convert_hebrew_to_english("׳") == ";"


class TestEnglishToHebrew:
    """English → Hebrew conversion (by physical key position)."""

    def test_how_to_hebrew(self):
        # h→י, o→ם, w→'  (same key positions)
        assert convert_english_to_hebrew("how") == "ים'"

    def test_simple_words(self):
        # c→ב, a→ש, t→א;  c→ב, t→א, v→ה
        assert convert_english_to_hebrew("cat") == "בשא"
        # c→ב, t→א, v→ה  (physical keys)
        assert convert_english_to_hebrew("ctv") == "באה"

    def test_preserves_spaces(self):
        # a→ש, b→נ
        assert convert_english_to_hebrew("a b") == "ש נ"

    def test_punctuation(self):
        assert convert_english_to_hebrew(";") == "׳"
        assert convert_english_to_hebrew(".") == "ץ"

    def test_unknown_chars_unchanged(self):
        assert convert_english_to_hebrew("123") == "123"


class TestConvertAuto:
    """Auto-detection: mostly Hebrew → to English; mostly English → to Hebrew."""

    def test_mostly_hebrew_converts_to_english(self):
        # Hebrew text -> convert to English
        result = convert_auto("שלום")
        assert result == "akuo"

    def test_mostly_english_converts_to_hebrew(self):
        # English text -> convert to Hebrew
        result = convert_auto("hello")
        assert result == "יקךךם"

    def test_mixed_english_majority_converts_to_hebrew(self):
        result = convert_auto("hello ש")
        # More English letters -> convert to Hebrew: "hello " -> "יקךךם ", ש stays
        assert result == "יקךךם ש"

    def test_mixed_hebrew_majority_converts_to_english(self):
        result = convert_auto("שלום hi")
        # More Hebrew -> convert to English
        assert result == "akuo hi"

    def test_empty_unchanged(self):
        assert convert_auto("") == ""
        assert convert_auto("   ") == "   "

    def test_no_letters_unchanged(self):
        assert convert_auto("123!@#") == "123!@#"
