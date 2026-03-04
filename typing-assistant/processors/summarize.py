"""Summarize text into a shorter version."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT

_PROMPT = """Summarize the following text into a shorter version.
Return only the summary.

Text:
{text}
"""


def summarize_text(text: str) -> str:
    """Summarize text into a shorter version. Returns only the summary."""
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
