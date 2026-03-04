"""Basic tests for AI processors. Require OPENAI_API_KEY for full runs."""

from processors.rewrite import rewrite_text
from processors.summarize import summarize_text


def test_rewrite():
    result = rewrite_text("i need terraform for eks")
    assert isinstance(result, str)
    assert len(result) > 0


def test_summary():
    text = "Kubernetes manages containerized workloads."
    result = summarize_text(text)
    assert isinstance(result, str)
    assert len(result) > 0
