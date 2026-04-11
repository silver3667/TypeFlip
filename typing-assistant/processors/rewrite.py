"""Rewrite text to be clearer and more professional. Bilingual (English + Hebrew)."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """Rewrite the following sentence to be clearer and more professional.
Return only the rewritten sentence.

Text:
{text}
"""

_HEBREW_PROMPT = """כתוב מחדש את המשפט הבא כך שיהיה ברור ומקצועי יותר.
אל תתרגם לאנגלית. השאר הכל בעברית.
החזר רק את המשפט המשוכתב.

טקסט:
{text}
"""


def rewrite_text(text: str) -> str:
    """Rewrite text to be clearer and more professional.

    Auto-detects Hebrew or English and uses the appropriate prompt.
    """
    if not text or not text.strip():
        return text
    if not OPENAI_API_KEY:
        return text
    prompt = _HEBREW_PROMPT if is_hebrew(text) else _ENGLISH_PROMPT
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
    response = client.chat.completions.create(
        model=PROMPT_MODEL,
        messages=[
            {"role": "user", "content": prompt.format(text=text.strip())},
        ],
        max_tokens=500,
    )
    result = (response.choices[0].message.content or "").strip()
    return result if result else text
