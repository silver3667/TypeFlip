# Hebrew / English Typing Fix

A small set of background daemons for Windows and Linux that fix the two most
annoying things that happen when you type in a mix of Hebrew and English:

1. **Wrong keyboard layout.** You wanted `how are things` but typed
   `ctv`, `ukh`, `n,fbho` (or the opposite direction). Press a hotkey and it
   is instantly converted by physical key position, using the standard
   Israeli **SI-1452** layout.
2. **Spelling and grammar mistakes** — in **both** Hebrew and English. Press a
   hotkey and the last sentence is fixed in place, in its original language.

The rest (rewrite / summarize / expand into a prompt / optimize prompt) is
English-only AI sugar on top. Hebrew input is intentionally skipped for those
tools so you never end up with a surprise English translation of your Hebrew
text.

## What's in the repo

There are three independent daemons you can run. Pick whichever fits your
workflow — they don't need to run together.

| Folder | Hotkey | Uses clipboard | AI | Best for |
|---|---|---|---|---|
| `layout_fix/` (root)     | `Ctrl+Alt+T`      | Yes (Select All → Copy → Paste) | No | Fixing a whole field at once |
| `layout-fix-daemon/`     | `Ctrl+;`          | No (rolling keystroke buffer) | No | Fixing just what you typed |
| `typing-assistant/`      | `Ctrl+;` and more | No | Yes (OpenAI) | Full experience: layout + spelling + prompt helpers |

`typing-assistant/` is the main one. The other two are simpler, dependency-light
alternatives if you just want layout conversion and nothing else.

## Quick start (typing-assistant)

```bash
cd typing-assistant
pip install -r requirements.txt
set OPENAI_API_KEY=your_key_here   # optional; only needed for the AI features
python run_daemon.py
```

On Windows you can also just double-click `typing-assistant\run_daemon.bat`,
which launches the daemon with `pythonw` so there is no console window.

### Hotkeys (typing-assistant)

| Shortcut             | Action                                               |
|----------------------|------------------------------------------------------|
| `Ctrl + ;`           | Fix keyboard layout (Hebrew ↔ English)               |
| `Ctrl + Shift + ;`   | Fix spelling / grammar (Hebrew and English)          |
| `Ctrl + Alt + ;`     | Fix layout, then fix typos                           |
| `Ctrl + .`           | Quick fix = layout + typos in one go                 |
| `Ctrl + Enter`       | Optimize the last sentence as an AI prompt *(EN)*    |
| `Alt + Enter`        | Rewrite the last sentence more clearly *(EN)*        |
| `Ctrl + /`           | Summarize the last sentence *(EN)*                   |
| `Ctrl + Shift+Enter` | Expand the last idea into a full AI prompt *(EN)*    |

*(EN)* = English only. If you trigger these on Hebrew text, the daemon prints
`skipped: Hebrew not supported` and leaves your text alone.

## Always on at login (Windows)

No registry edits, no admin rights, no Task Scheduler — just the normal
Windows user Startup folder:

1. Press `Win + R`, type `shell:startup`, press Enter.
2. Right-click inside that folder → **New → Shortcut**.
3. Point the shortcut at `typing-assistant\run_daemon.bat` (or whichever of
   the three daemons you picked).
4. Done. It will start silently every time you log in.

To remove it, delete the shortcut from that folder.

## Spelling fix — how it stays in the right language

The typo corrector looks at the text first. If it's mostly Hebrew letters it
uses a Hebrew prompt that explicitly says *do not translate, return Hebrew*.
If it's mostly English it uses the English prompt. So `שלןם עולם` becomes
`שלום עולם`, and `helo wrld` becomes `hello world`.

## Layout mapping — SI-1452

Conversion is done by **physical key position**, not by transliteration.
Example:

- Hebrew `ים'` (keys at positions h, o, w) → `how`
- English `how` → `ים'`
- Hebrew `ctv ukh n,fbho` → `how are things`

## Requirements

- Python 3.11+
- Windows 10/11 or Linux (graphical session, not SSH)
- Dependencies: `pynput`, `keyboard`, `pyperclip`, `openai`, `pytest`
- `OPENAI_API_KEY` environment variable — only needed for the AI-powered tools
  (spelling fix, rewrite, summarize, expand, optimize)

## Run the tests

```bash
# layout conversion tests (root)
pytest tests/ -v

# buffer-based daemon tests
pytest layout-fix-daemon/tests/ -v

# typing-assistant processor tests (needs OPENAI_API_KEY)
pytest typing-assistant/tests/ -v
```

## Safety notes

- The daemons only send **local keystrokes** (backspace, typing, clipboard) to
  whichever window has focus. They don't capture, log, or upload your
  keystrokes anywhere.
- The typing-assistant buffer keeps the last 200 characters in memory only,
  and is wiped when the daemon exits. It is never written to disk.
- The AI features only run when you press the matching hotkey, and they only
  send the **last sentence** — not the whole buffer — to OpenAI.
- The daemon does not modify any system settings, registry entries, startup
  entries, or permissions. Autostart is opt-in via a shortcut you place
  yourself.

## License

MIT.
