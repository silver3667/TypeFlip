"""Configuration for the typing assistant daemon."""

import os

DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
MODEL_NAME: str = "gpt-4o-mini"      # typo correction (F2) — simple task, mini is fine
PROMPT_MODEL: str = "gpt-4o"          # all other AI features (F3-F7) — needs quality
MAX_BUFFER_SIZE: int = 200
OPENAI_TIMEOUT: float = 15.0
