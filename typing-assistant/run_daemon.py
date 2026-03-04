#!/usr/bin/env python3
"""Entry point for the typing assistant daemon."""

import os
import sys

# Ensure project root is on path when run as script
_root = os.path.dirname(os.path.abspath(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from daemon.daemon import run_daemon

if __name__ == "__main__":
    run_daemon()
