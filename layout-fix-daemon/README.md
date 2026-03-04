# Layout Fix Daemon

Fixes text typed in the wrong keyboard layout (Hebrew ↔ English) **without using the clipboard**.

When you type with the wrong layout active, press **Ctrl+;** to convert the last typed text to the correct layout.

## How it works

- A background process records the last **200** characters you type into a rolling buffer.
- When you press **Ctrl+;**, the daemon:
  1. Reads the recent buffer
  2. Detects whether the text is mostly Hebrew or mostly English
  3. Converts to the other layout (Hebrew → English or English → Hebrew) by physical key position
  4. Deletes the original characters (backspace)
  5. Types the corrected text

No clipboard is used; everything is done by simulating backspace and key presses.

## Installation

```bash
cd layout-fix-daemon
pip install -r requirements.txt
```

## Running the daemon

```bash
python run_daemon.py
```

On Linux, global keyboard access usually requires root or appropriate permissions:

```bash
sudo python run_daemon.py
```

Or run as your user and grant access to the input device (e.g. add yourself to the `input` group).

**Stop the daemon:** Press `Ctrl+C`.

## Layout mapping

Conversion uses the standard **Israeli SI-1452** Hebrew keyboard layout: each physical key is mapped between English (QWERTY) and Hebrew by position. For example:

- **Hebrew → English:** `ים'` (keys for h, o, w in Hebrew) → `how`
- **English → Hebrew:** `how` → `ים'`

Auto-detection:

- If the text is **mostly Hebrew** characters → convert to English.
- If the text is **mostly English** (or mixed) → convert to Hebrew.

## Project structure

```
layout-fix-daemon/
├── layout_fix/
│   ├── __init__.py
│   ├── daemon.py      # Main daemon loop and hotkey handler
│   ├── key_buffer.py  # Rolling buffer of typed characters
│   ├── converter.py   # Hebrew ↔ English layout conversion
│   └── hotkeys.py     # Hotkey registration and key simulation
├── tests/
│   └── test_converter.py
├── requirements.txt
├── README.md
└── run_daemon.py
```

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

## Dependencies

- **keyboard** – global hotkey (Ctrl+;) and simulating backspace/typing
- **pynput** – recording typed characters
- **pytest** – tests

## Notes

- The daemon only corrects the **last** segment of typed text (up to 200 characters). For long text, trigger the hotkey soon after typing the wrong part.
- Backspace is reflected in the buffer: if you backspace before pressing the hotkey, the corrected text will match what’s actually on screen (within the buffer window).
