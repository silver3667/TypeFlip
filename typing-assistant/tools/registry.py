"""Tool registry: map tool names to processor functions. First step toward an AI brain."""

from processors.rewrite import rewrite_text
from processors.summarize import summarize_text
from processors.expand_prompt import expand_prompt
from processors.prompt_optimizer import optimize_prompt
from processors.quick_fix import quick_fix

TOOLS = {
    "rewrite": rewrite_text,
    "summarize": summarize_text,
    "expand_prompt": expand_prompt,
    "optimize_prompt": optimize_prompt,
    "quick_fix": quick_fix,
}
