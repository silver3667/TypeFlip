"""Optimize free-form text into a clear prompt for AI assistants."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT

_PROMPT = """You improve prompts for AI systems.

Rewrite the following text to be a clear, well-structured prompt for an AI assistant.
Do not add explanations.
Return only the improved prompt.

Text:
{text}
"""


def optimize_prompt(text: str) -> str:
    """Rewrite text as a clear, well-structured prompt for AI. Returns only the improved prompt."""
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
