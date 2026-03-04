"""Main daemon: register hotkey and run until interrupted."""

from layout_fix.hotkeys import fix_layout, register_hotkey, wait_forever


def run() -> None:
    """Start the keyboard layout fix daemon.

    Registers Ctrl+Alt+T and blocks until the process is stopped.
    """
    print("Keyboard Layout Fix Daemon running...")
    print("Hotkey: CTRL + ALT + T")
    print("Press Ctrl+C to exit.")
    register_hotkey(fix_layout)
    wait_forever()


if __name__ == "__main__":
    run()
