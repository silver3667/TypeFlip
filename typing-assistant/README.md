# Typing Assistant

The full-featured daemon: Hebrew/English layout fix, AI typo correction, and
prompt-shaping tools — all triggered by global hotkeys on selected text.

For setup, install instructions, autostart, and full troubleshooting see the
**[top-level README](../README.md)**. This file documents only what's specific
to the `typing-assistant/` daemon.

## Hotkeys

Select text first, then press:

| Shortcut    | Action                                          |
|-------------|-------------------------------------------------|
| `Shift+F1`  | Fix keyboard layout (Hebrew ↔ English)          |
| `Shift+F2`  | Fix spelling / grammar (Hebrew and English)     |
| `Shift+F3`  | Rewrite text more professionally *(EN only)*    |
| `Shift+F4`  | Summarize text *(EN only)*                      |
| `Shift+F5`  | Optimize text as an AI prompt *(EN only)*       |
| `Shift+F6`  | Expand idea into a full AI prompt *(EN only)*   |
| `Shift+F7`  | Humanize AI-sounding text *(EN only)*           |

## Environment variables

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | Required for everything except `Shift+F1` (layout fix is offline). |
| `PROMPT_MODEL` | OpenAI model used for prompt-shaping tools. Default: `gpt-4o-mini`. |
| `TYPING_ASSISTANT_LOG` | Override log file path. Default: `~/.typing-assistant/daemon.log`. |
| `TYPING_ASSISTANT_NATIVE_PASTE` | Set to `1` to send `Ctrl+V` via Win32 `SendInput` instead of the `keyboard` library. Use this if you see duplicated/odd pastes on a non-English active layout. |
| `TYPING_ASSISTANT_TRACE` | Set to `1` to log every raw keyboard event to the log file. **Logs every keystroke including passwords** — only enable while diagnosing a bug, then disable. |

## Logs

The daemon writes to `~/.typing-assistant/daemon.log` (rotated at 1 MB, 3
backups). Each hotkey invocation gets a 6-character call ID so you can trace
a single press through copy → process → paste.

## Singleton

Only one daemon can run at a time — the second instance will print
`ANOTHER DAEMON IS ALREADY RUNNING` and exit. This prevents the most common
double-paste bug (two daemons both responding to the same hotkey). When run
as administrator the lock is machine-wide; when run unelevated it falls back
to per-session, so a `pythonw.exe` zombie from a different logon session may
go undetected. If pastes start duplicating, see the Troubleshooting section
in the top-level README.

## Run

```bash
python run_daemon.py
```

Or on Windows, right-click `run_daemon.bat` → **Run as administrator**.

## Tests

```bash
pytest typing-assistant/tests/ -v
```

The tests assume `OPENAI_API_KEY` is set; processor tests will skip without it.
