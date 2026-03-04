"""Global hotkey registration for layout fix, typo correction, and prompt optimization."""

from collections.abc import Callable

from pynput import keyboard


def register_hotkeys(
    on_layout: Callable[[], None],
    on_typo: Callable[[], None],
    on_layout_then_typo: Callable[[], None],
    on_prompt_optimize: Callable[[], None],
    on_rewrite: Callable[[], None],
    on_summarize: Callable[[], None],
    on_expand_prompt: Callable[[], None],
    on_quick_fix: Callable[[], None],
) -> keyboard.GlobalHotKeys:
    """
    Register the hotkeys and return the hotkey listener.
    - CTRL + ;               -> on_layout (fix keyboard layout)
    - CTRL + SHIFT + ;       -> on_typo (fix typos with AI)
    - CTRL + ALT + ;         -> on_layout_then_typo (layout then typo)
    - CTRL + ENTER           -> on_prompt_optimize (optimize prompt for AI)
    - ALT + ENTER            -> on_rewrite (rewrite text)
    - CTRL + /               -> on_summarize (summarize text)
    - CTRL + SHIFT + ENTER   -> on_expand_prompt (expand into AI prompt)
    - CTRL + .               -> on_quick_fix (quick fix: layout + typos)
    """
    return keyboard.GlobalHotKeys(
        {
            "<ctrl>+;": on_layout,
            "<ctrl>+<shift>+;": on_typo,
            "<ctrl>+<alt>+;": on_layout_then_typo,
            "<ctrl>+<enter>": on_prompt_optimize,
            "<alt>+<enter>": on_rewrite,
            "<ctrl>+/": on_summarize,
            "<ctrl>+<shift>+<enter>": on_expand_prompt,
            "<ctrl>+.": on_quick_fix,
        }
    )
