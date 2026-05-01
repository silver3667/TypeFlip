"""Expand an idea into a clear prompt for an AI assistant. Bilingual (English + Hebrew)."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """Expand the user's short idea below into a complete, ready-to-use prompt for an AI assistant.

The expanded prompt should:
- Set the role/context the AI should adopt
- State the goal concretely (what success looks like)
- List the specific things the AI should produce or address
- Note any constraints (length, tone, audience, format)

Rules for your reply:
- Output ONLY the expanded prompt itself, written as if the user is speaking to the AI. No preamble ("Here is...", "Certainly!"), no postamble, no meta-explanation of what the prompt does, no markdown fences, no placeholders like [AI Assistant Name] or [Your Name].
- Do not invent personal details the user didn't provide. Keep it generic enough to use as-is.
- Keep it tight. Aim for 6-15 lines.

User's idea:
{text}
"""

_HEBREW_PROMPT = """הרחב את הרעיון הקצר של המשתמש לפרומפט מלא ומוכן לשימוש עבור עוזר AI.

הפרומפט המורחב צריך:
- לקבוע את התפקיד/ההקשר ש-AI צריך לאמץ
- לנסח את המטרה באופן קונקרטי (איך נראית הצלחה)
- לפרט את הדברים הספציפיים ש-AI צריך לייצר או להתייחס אליהם
- לציין אילוצים (אורך, טון, קהל, פורמט)

כללים לתשובה שלך:
- החזר רק את הפרומפט המורחב עצמו, כתוב כאילו המשתמש מדבר ל-AI. ללא הקדמה ("הנה...", "בוודאי!"), ללא סיום, ללא הסבר מטא על מה הפרומפט עושה, ללא בלוקי קוד, ללא מציינים כמו [שם העוזר] או [שמך].
- אל תמציא פרטים אישיים שהמשתמש לא נתן. שמור על כלליות שמאפשרת שימוש כמו שהוא.
- שמור על תמציתיות. שאף ל-6 עד 15 שורות.
- אל תתרגם לאנגלית. כתוב בעברית.

הרעיון של המשתמש:
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
