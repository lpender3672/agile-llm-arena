from .openai_compat import OpenAICompatProvider


class LocalOllamaProvider(OpenAICompatProvider):
    """
    Self-hosted models via Ollama's OpenAI-compatible endpoint.
    No API key required. token_cost = 0; use score_per_second as the
    efficiency proxy rather than score_per_1k_tokens.
    Requires: ollama serve  with the target model already pulled.
    """

    def __init__(self, model_id: str, base_url: str = "http://localhost:11434/v1"):
        from openai import AsyncOpenAI
        super().__init__(
            AsyncOpenAI(base_url=base_url, api_key="ollama"),
            model_id,
        )
