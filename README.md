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

## Setup (Windows)

### 1. Clone and install

```bash
git clone https://github.com/silverdeath366/hebrew-english-fix.git
cd hebrew-english-fix/typing-assistant
pip install -r requirements.txt
```

### 2. Set your OpenAI key (optional — only needed for AI features)

Open a terminal **as administrator** and run:

```bash
setx OPENAI_API_KEY "your_key_here"
```

This sets it permanently. Restart your terminal for it to take effect.

### 3. Run it

**Right-click** `typing-assistant\run_daemon.bat` → **Run as administrator**.

> **Why admin?** The `keyboard` library needs admin privileges on Windows to
> capture global hotkeys. Without it, hotkeys won't work.

### 4. Use it

1. Type or select some text in any app
2. **Select the text** (`Ctrl+A` or drag to highlight)
3. Press the hotkey (see table below)
4. The text is replaced in place

### 5. Auto-start on login (optional)

1. Press `Win+R`, type `shell:startup`, press Enter.
2. Right-click inside that folder → **New → Shortcut**.
3. Point the shortcut at `typing-assistant\run_daemon.bat`.
4. Right-click the new shortcut → **Properties** → **Advanced** → check **Run as administrator** → OK.
5. Done. It will start silently (with an admin prompt) every time you log in.

## Hotkeys

Select text first, then press:

| Shortcut      | Action                                          |
|---------------|-------------------------------------------------|
| `Shift+F1`    | Fix keyboard layout (Hebrew ↔ English)          |
| `Shift+F2`    | Fix spelling / grammar (Hebrew and English)     |
| `Shift+F3`    | Rewrite text more professionally *(EN only)*    |
| `Shift+F4`    | Summarize text *(EN only)*                      |
| `Shift+F5`    | Optimize text as an AI prompt *(EN only)*       |
| `Shift+F6`    | Expand idea into a full AI prompt *(EN only)*   |
| `Shift+F7`    | Humanize AI-sounding text *(EN only)*           |

*(EN only)* = English only. If you trigger these on Hebrew text, the daemon
skips it and leaves your text alone.

## What's in the repo

There are three independent daemons. Pick whichever fits your workflow — they
don't need to run together.

| Folder | Uses clipboard | AI | Best for |
|---|---|---|---|
| `layout_fix/` (root)     | Yes (Select All → Copy → Paste) | No | Fixing a whole field at once |
| `layout-fix-daemon/`     | No (rolling keystroke buffer) | No | Fixing just what you typed |
| `typing-assistant/`      | Yes (select → hotkey → replaced) | Yes (OpenAI) | Full experience: layout + spelling + AI tools |

`typing-assistant/` is the main one. The other two are simpler, dependency-light
alternatives if you just want layout conversion and nothing else.

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
- **Administrator privileges** (required for global hotkey capture)
- Dependencies: `keyboard`, `pynput`, `pyperclip`, `openai`
- `OPENAI_API_KEY` environment variable — only needed for the AI-powered tools
  (spelling fix, rewrite, summarize, expand, optimize, humanize)

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
  send the **selected text** to OpenAI.
- The daemon does not modify any system settings, registry entries, startup
  entries, or permissions. Autostart is opt-in via a shortcut you place
  yourself.

## Troubleshooting

### Numbers turn into symbols (!@#$%…) and scrolling stops working

This means the Shift key is being captured globally. It was caused by an old
bug where hotkeys were registered with `suppress=True`. This was fixed in
commit `00ff08f`.

**If it happens to you:**

1. Open Task Manager and kill all `pythonw.exe` / `python.exe` processes
   running the daemon.
2. Make sure you have the latest code (`git pull`).
3. Restart the daemon: double-click `typing-assistant\run_daemon.bat`.

**For developers:** never set `suppress=True` on `keyboard.add_hotkey()` for
hotkeys that use a modifier key (Shift, Ctrl, Alt). The `keyboard` library
will swallow that modifier globally, breaking normal typing.

## License

MIT. See [LICENSE](LICENSE).
