"""Rewrite text to be clearer and more professional."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT

_PROMPT = """Rewrite the following sentence to be clearer and more professional.
Return only the rewritten sentence.

Text:
{text}
"""


def rewrite_text(text: str) -> str:
    """Rewrite text to be clearer and more professional. Returns only the rewritten sentence."""
    if not text or not text.strip():
        return text
    if not OPENAI_API_KEY:
        return text
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
    response = client.chat.completions.create(
        model=PROMPT_MODEL,
        messages=[
            {"role": "user", "content": _PROMPT.format(text=text.strip())},
        ],
        max_tokens=500,
    )
    result = (response.choices[0].message.content or "").strip()
    return result if result else text
