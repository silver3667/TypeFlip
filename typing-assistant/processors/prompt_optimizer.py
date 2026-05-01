"""Optimize free-form text into a clear prompt for AI assistants. Bilingual (English + Hebrew)."""

from openai import OpenAI

from config.settings import OPENAI_API_KEY, PROMPT_MODEL, OPENAI_TIMEOUT
from processors.layout_converter import is_hebrew

_ENGLISH_PROMPT = """Rewrite the user's text below into a sharp, well-structured prompt for an AI assistant.

The improved prompt MUST specify:
- Role: who the AI should act as (if relevant)
- Task: the concrete deliverable, in one clear sentence
- Constraints: length, audience, tone, what to avoid
- Format: how the output should be structured (bullets, sections, code, etc.)

Rules for your reply:
- Output ONLY the improved prompt itself. No preamble ("Here is...", "Certainly!"), no postamble, no meta-commentary, no markdown fences, no quotation marks around the prompt.
- Do not invent facts the user didn't give. If something is unspecified (e.g. audience), make a reasonable default and bake it into the prompt — don't ask the user.
- Keep it tight. Aim for 4-10 lines.

User's text:
{text}
"""

_HEBREW_PROMPT = """כתוב מחדש את הטקסט של המשתמש לפרומפט חד ומובנה עבור עוזר AI.

הפרומפט המשופר חייב לכלול:
- תפקיד: מי ה-AI צריך לגלם (אם רלוונטי)
- משימה: התוצר הקונקרטי, במשפט ברור אחד
- אילוצים: אורך, קהל יעד, טון, מה להימנע ממנו
- פורמט: איך התשובה צריכה להיות מובנית (נקודות, סעיפים, קוד וכו')

כללים לתשובה שלך:
- החזר רק את הפרומפט המשופר עצמו. ללא הקדמה ("הנה...", "בוודאי!"), ללא סיום, ללא הערות מטא, ללא בלוקי קוד, ללא מירכאות סביב הפרומפט.
- אל תמציא עובדות שהמשתמש לא נתן. אם משהו לא צוין (למשל קהל), קבע ברירת מחדל סבירה והכנס אותה לפרומפט — אל תשאל את המשתמש.
- שמור על תמציתיות. שאף ל-4 עד 10 שורות.
- אל תתרגם לאנגלית. כתוב בעברית.

הטקסט של המשתמש:
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
