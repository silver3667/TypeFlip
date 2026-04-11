"""Expand an idea into a clear prompt for an AI assistant. Bilingual (English + Hebrew)."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """Expand the following idea into a clear prompt for an AI assistant.

Text:
{text}
"""

_HEBREW_PROMPT = """הרחב את הרעיון הבא לפרומפט ברור עבור עוזר AI.
אל תתרגם לאנגלית. כתוב את הפרומפט בעברית.

טקסט:
{text}
"""


def expand_prompt(text: str) -> str:
    """Expand an idea into a clear prompt for an AI assistant.

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
