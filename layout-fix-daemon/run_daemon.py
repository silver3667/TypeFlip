#!/usr/bin/env python3
"""
Run the layout-fix daemon. Requires root on Linux for global keyboard capture.
"""

import os
import sys

# Ensure layout_fix package is importable
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from layout_fix.daemon import run_daemon

if __name__ == "__main__":
    print("Layout-fix daemon started. Hotkey: Ctrl+;")
    print("Press Ctrl+C to stop.")
    run_daemon()
