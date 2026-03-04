"""Configuration for the typing assistant daemon."""

import os

DEBUG: bool = True
OPENAI_API_KEY: str = os.environ.get("OPENAI_API_KEY", "")
MODEL_NAME: str = "gpt-4o-mini"
PROMPT_MODEL: str = "gpt-4o-mini"
MAX_BUFFER_SIZE: int = 200
OPENAI_TIMEOUT: float = 5.0
