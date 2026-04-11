"""Global hotkey registration using the 'keyboard' library (works reliably on Windows)."""

from collections.abc import Callable

import keyboard


def register_hotkeys(
    on_layout: Callable[[], None],
    on_typo: Callable[[], None],
    on_rewrite: Callable[[], None],
    on_summarize: Callable[[], None],
    on_prompt_optimize: Callable[[], None],
    on_expand_prompt: Callable[[], None],
    on_humanize: Callable[[], None],
) -> None:
    """
    Register the hotkeys using the keyboard library.
    - Shift + F1  -> on_layout (fix keyboard layout)
    - Shift + F2  -> on_typo (fix typos with AI)
    - Shift + F3  -> on_rewrite (rewrite text professionally)
    - Shift + F4  -> on_summarize (summarize text)
    - Shift + F5  -> on_prompt_optimize (optimize prompt for AI)
    - Shift + F6  -> on_expand_prompt (expand into AI prompt)
    - Shift + F7  -> on_humanize (humanize AI text)
    """
    keyboard.add_hotkey('shift+f1', on_layout, suppress=True)
    keyboard.add_hotkey('shift+f2', on_typo, suppress=True)
    keyboard.add_hotkey('shift+f3', on_rewrite, suppress=True)
    keyboard.add_hotkey('shift+f4', on_summarize, suppress=True)
    keyboard.add_hotkey('shift+f5', on_prompt_optimize, suppress=True)
    keyboard.add_hotkey('shift+f6', on_expand_prompt, suppress=True)
    keyboard.add_hotkey('shift+f7', on_humanize, suppress=True)
