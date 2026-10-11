import os

import anthropic
from dotenv import load_dotenv
from loguru import logger

MAX_TOKENS = 1000
PROMPT = "Say hello in French."

# Pricing page: https://platform.claude.com/docs/en/about-claude/pricing
# Fill in with the right prices
PRICES = {
    "anthropic/claude-haiku-4.5": {"input": 0.00, "output": 0.00},
    "anthropic/claude-sonnet-5.5": {"input": 0.00, "output": 00.00},
}

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY is not set (check your .env file)")

client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api",
    auth_token=OPENROUTER_API_KEY,
)
messages = [{"role": "user", "content": PROMPT}]


def cost_usd(model, input_tokens, output_tokens):
    price = PRICES[model]  # noqa: F841


def main():
    model = "anthropic/claude-haiku-4.5"

    logger.info("TODO calculate input message cost")
    logger.info("TODO calculate output max cost, using MAX_TOKENS")

    # Actual cost
    response = client.messages.create(  # noqa: F841
        model=model, max_tokens=MAX_TOKENS, messages=messages
    )

    logger.info("TODO calculate actual cost")


if __name__ == "__main__":
    main()
