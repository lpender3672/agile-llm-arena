import os

from .openai_compat import OpenAICompatProvider


class OpenRouterProvider(OpenAICompatProvider):
    """
    OpenRouter via OpenAI-compatible API with full tool-calling loop.
    Requires: pip install openai  and  OPENROUTER_API_KEY env var.
    """

    def __init__(self, model_id: str):
        from openai import AsyncOpenAI
        super().__init__(
            AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=os.environ["OPENROUTER_API_KEY"],
            ),
            model_id,
        )
