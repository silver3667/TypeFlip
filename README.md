# Keyboard Layout Fix Daemon

A small background daemon that fixes text typed in the wrong keyboard layout (Hebrew ↔ English). Press a hotkey to convert the current text in the focused control.

## Example

You type:

```
ctv ukh n,fbho
```

but you meant **"how are things"** with the keyboard set to English. The daemon converts using the physical key positions (Hebrew layout → English).

## Requirements

- Python 3.11+
- Linux or Windows

## Installation

```bash
pip install -r requirements.txt
```

## Run

From the project root:

```bash
python run_daemon.py
```

Or run the daemon module directly:

```bash
python -m layout_fix.daemon
```

Output:

```
Keyboard Layout Fix Daemon running...
Hotkey: CTRL + ALT + T
Press Ctrl+C to exit.
```

## Hotkey usage

1. Focus the text field (editor, input, etc.) that contains the wrong-layout text.
2. Press **Ctrl + Alt + T**.
3. The daemon will:
   - Select all (Ctrl+A)
   - Copy (Ctrl+C)
   - Detect whether the text is mostly Hebrew or English
   - Convert (Hebrew → English or English → Hebrew)
   - Paste the corrected text (Ctrl+V)

No need to select the text manually; the hotkey selects all, converts, and replaces.

## Linux and Windows

- **Linux**: The daemon tries the `keyboard` library first. If it fails (e.g. “must be root”), it automatically falls back to **pynput**, which usually works without sudo when a graphical session (X/Wayland) is running. So on a normal desktop you typically do **not** need to run with `sudo`.
- **Windows**: Usually works without admin; the `keyboard` library is used.
- **Headless/SSH**: The daemon needs a display and a keyboard; it will not run over SSH without a display.

## Tests

```bash
pytest tests/ -v
```

## Project structure

```
layout-fix-daemon/
├── layout_fix/
│   ├── __init__.py
│   ├── daemon.py      # Main loop, starts daemon and registers hotkeys
│   ├── converter.py   # Hebrew ↔ English conversion
│   ├── detector.py    # Detect layout (hebrew / english)
│   └── hotkeys.py     # Global hotkey Ctrl+Alt+T, fix_layout()
├── tests/
│   └── test_converter.py
├── requirements.txt
├── README.md
└── run_daemon.py
```
