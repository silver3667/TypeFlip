"""Optimize free-form text into a clear prompt for AI assistants. Bilingual (English + Hebrew)."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """You improve prompts for AI systems.

Rewrite the following text to be a clear, well-structured prompt for an AI assistant.
Do not add explanations.
Return only the improved prompt.

Text:
{text}
"""

_HEBREW_PROMPT = """אתה משפר פרומפטים עבור מערכות AI.

כתוב מחדש את הטקסט הבא כך שיהיה פרומפט ברור ומובנה עבור עוזר AI.
אל תוסיף הסברים. אל תתרגם לאנגלית.
החזר רק את הפרומפט המשופר.

טקסט:
{text}
"""


def optimize_prompt(text: str) -> str:
    """Rewrite text as a clear, well-structured prompt for AI.

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
