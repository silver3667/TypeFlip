"""Minimal OpenAI API wrapper for typo correction. Language-aware (English + Hebrew)."""

from openai import OpenAI

from config.settings import MODEL_NAME, OPENAI_API_KEY, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """Fix spelling and grammar in the following English text.
Do not change meaning. Do not translate.
Return only the corrected sentence.

TEXT:
{text}
"""

_HEBREW_PROMPT = """תקן שגיאות כתיב ודקדוק בטקסט העברי הבא.
אל תשנה את המשמעות. אל תתרגם לאנגלית.
החזר רק את המשפט המתוקן בעברית.

טקסט:
{text}
"""


def correct_text(text: str) -> str:
    """Fix spelling and grammar using the configured model.

    Picks a Hebrew or English prompt based on the text itself so Hebrew input
    stays in Hebrew and English input stays in English.
    """
    if not text or not text.strip():
        return text
    if not OPENAI_API_KEY:
        return text
    prompt = _HEBREW_PROMPT if is_hebrew(text) else _ENGLISH_PROMPT
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt.format(text=text.strip())},
        ],
        max_tokens=500,
    )
    result = (response.choices[0].message.content or "").strip()
    return result if result else text
