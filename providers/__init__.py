from .anthropic import AnthropicAPIProvider
from .base import Message, Provider, RunResult
from .claude_code import ClaudeCodeCLIProvider
from .ollama import LocalOllamaProvider
from .openrouter import OpenRouterProvider


def make_provider(provider_type: str, model_id: str, **kwargs) -> Provider:
    if provider_type == "claude_code_cli":
        return ClaudeCodeCLIProvider()
    elif provider_type == "anthropic_api":
        return AnthropicAPIProvider(model_id)
    elif provider_type == "openrouter":
        return OpenRouterProvider(model_id)
    elif provider_type == "ollama":
        return LocalOllamaProvider(model_id, **kwargs)
    raise ValueError(f"Unknown provider: {provider_type!r}")


__all__ = [
    "make_provider",
    "Provider",
    "RunResult",
    "Message",
    "AnthropicAPIProvider",
    "ClaudeCodeCLIProvider",
    "LocalOllamaProvider",
    "OpenRouterProvider",
]
