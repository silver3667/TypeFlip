"""Minimal OpenAI API wrapper for typo correction."""

from openai import OpenAI

from config.settings import MODEL_NAME, OPENAI_API_KEY, OPENAI_TIMEOUT

_PROMPT = """Fix spelling and grammar in the following text.
Do not change meaning.
Return only the corrected sentence.

TEXT:
{text}
"""


def correct_text(text: str) -> str:
    """Fix spelling and grammar using the configured model. Returns corrected text."""
    if not text or not text.strip():
        return text
    if not OPENAI_API_KEY:
        return text
    client = OpenAI(api_key=OPENAI_API_KEY, timeout=OPENAI_TIMEOUT)
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": _PROMPT.format(text=text.strip())},
        ],
        max_tokens=500,
    )
    result = (response.choices[0].message.content or "").strip()
    return result if result else text
