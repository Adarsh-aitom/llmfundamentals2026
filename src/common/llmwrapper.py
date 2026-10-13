import os
from dataclasses import dataclass
from typing import Literal

import anthropic
import openai
from dotenv import load_dotenv
from loguru import logger

Provider = Literal["anthropic", "openai"]

# Both providers go through OpenRouter: Claude with the Anthropic SDK, OpenAI with the OpenAI SDK.
OPENROUTER_ANTHROPIC_URL = "https://openrouter.ai/api"
OPENROUTER_OPENAI_URL = "https://openrouter.ai/api/v1"

DEFAULT_MODELS: dict[Provider, str] = {
    "anthropic": "anthropic/claude-haiku-4.5",
    "openai": "openai/gpt-4.1-mini",
}


@dataclass(frozen=True)
class LLMResponse:
    text: str
    input_tokens: int
    output_tokens: int
#    cost_usd: float | None  # None when the model's price is unknown # uncomment when you're working on the cost
    stop_reason: str | None = None  # e.g. "end_turn" or "max_tokens" (Claude), "stop" or "length" (OpenAI)
 #   latency_seconds: float | None = None  # wall-clock time of ask(), including retries # uncomment when you're working on the latency


class LLMWrapper:
    """Handles API connection to the chosen LLM."""

    def __init__(
        self,
        provider: Provider,
        model: str | None = None,
        max_tokens: int = 1000,
    ):
        if provider not in DEFAULT_MODELS:
            raise ValueError(f"Unknown provider: {provider!r}")

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is not set (check your .env file)")

        self.provider = provider
        self.model = model or DEFAULT_MODELS[provider]
        self.max_tokens = max_tokens
        self._anthropic = (
            anthropic.Anthropic(base_url=OPENROUTER_ANTHROPIC_URL, auth_token=api_key)
            if provider == "anthropic"
            else None
        )
        self._openai = (
            openai.OpenAI(base_url=OPENROUTER_OPENAI_URL, api_key=api_key)
            if provider == "openai"
            else None
        )

    def ask(self, prompt: str, system: str | None = None) -> LLMResponse:
        """Send a single prompt and return the text and the token usage."""
        logger.debug("Sending request to {}/{}", self.provider, self.model)
        if self.provider == "anthropic":
            return self._ask_anthropic(prompt, system)
        return self._ask_openai(prompt, system)

    def _ask_anthropic(self, prompt: str, system: str | None) -> LLMResponse:
        kwargs = {"system": system} if system else {}
        response = self._anthropic.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[{"role": "user", "content": prompt}],
            **kwargs,
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(f"Claude refused the request: {response.stop_details}")
        return LLMResponse(
            text="".join(b.text for b in response.content if b.type == "text"),
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
        )

    def _ask_openai(self, prompt: str, system: str | None) -> LLMResponse:
        # TODO implement function
        return LLMResponse(
            text="",
            input_tokens=0,
            output_tokens=0,
            stop_reason="",
        )


if __name__ == "__main__":
    # allows to quickly check that LLMWrapper works
    load_dotenv()  # reads OPENROUTER_API_KEY from the .env file
    for provider in ("anthropic", "openai"):
        llm = LLMWrapper(provider)
        logger.info("{}: {}", provider, llm.ask("Say hello in French."))
