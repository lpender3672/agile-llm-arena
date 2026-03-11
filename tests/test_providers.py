import os
from unittest.mock import MagicMock, patch

import pytest

from providers import make_provider
from providers.anthropic import AnthropicAPIProvider
from providers.base import RunResult
from providers.claude_code import ClaudeCodeCLIProvider
from providers.ollama import LocalOllamaProvider
from providers.openrouter import OpenRouterProvider


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def test_make_provider_unknown_raises():
    with pytest.raises(ValueError, match="Unknown provider"):
        make_provider("bogus", "model-x")


def test_make_provider_claude_code_cli():
    provider = make_provider("claude_code_cli", "")
    assert isinstance(provider, ClaudeCodeCLIProvider)


def test_make_provider_anthropic():
    with patch.dict("sys.modules", {"anthropic": MagicMock()}):
        provider = make_provider("anthropic_api", "claude-3-5-sonnet-20241022")
    assert isinstance(provider, AnthropicAPIProvider)


def test_make_provider_ollama():
    with patch.dict("sys.modules", {"openai": MagicMock()}):
        provider = make_provider("ollama", "qwen2.5-coder:7b")
    assert isinstance(provider, LocalOllamaProvider)


def test_make_provider_openrouter():
    os.environ.setdefault("OPENROUTER_API_KEY", "test-key")
    with patch.dict("sys.modules", {"openai": MagicMock()}):
        provider = make_provider("openrouter", "mistral/devstral-small")
    assert isinstance(provider, OpenRouterProvider)


def test_make_provider_ollama_custom_base_url():
    with patch.dict("sys.modules", {"openai": MagicMock()}):
        provider = make_provider("ollama", "llama3.2", base_url="http://myserver:11434/v1")
    assert isinstance(provider, LocalOllamaProvider)


# ---------------------------------------------------------------------------
# RunResult
# ---------------------------------------------------------------------------

def test_run_result_defaults():
    r = RunResult(
        output="ok", input_tokens=10, output_tokens=20,
        total_tokens=30, duration_seconds=1.5, turns=3,
    )
    assert r.error is None
    assert r.total_tokens == 30
    assert r.turns == 3


def test_run_result_with_error():
    r = RunResult("", 0, 0, 0, 0.0, 0, error="timeout")
    assert r.error == "timeout"
