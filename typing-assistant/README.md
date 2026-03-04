# Typing Assistant

Hebrew/English keyboard layout fix and AI typo correction daemon.

## Installation

```bash
pip install -r requirements.txt
```

## Environment variable

Set your OpenAI API key for typo correction:

```bash
export OPENAI_API_KEY=your_api_key_here
```

## Running the daemon

```bash
python run_daemon.py
```

## Hotkeys

| Shortcut           | Action                          |
|--------------------|----------------------------------|
| **CTRL + ;**       | Fix keyboard layout (Hebrew ↔ English) |
| **CTRL + SHIFT + ;** | Fix typos and grammar using AI   |
| **CTRL + ALT + ;** | Fix layout first, then run typo correction |
| **CTRL + ENTER**   | Optimize prompt for AI          |

Layout conversion uses the SI-1452 physical key mapping. Typo correction uses `gpt-4o-mini` when `OPENAI_API_KEY` is set. Prompt optimization uses `PROMPT_MODEL` (default `gpt-4o-mini`) to rewrite the last typed sentence as a clear prompt for ChatGPT, Cursor, Claude, etc.
