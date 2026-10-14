"""
Estimate the cost of a request before sending it, then compute the real cost.
"""
import os
import anthropic
from dotenv import load_dotenv
from loguru import logger

MAX_TOKENS = 1000
PROMPT = "Say hello in French."

# Pricing page: https://platform.claude.com/docs/en/about-claude/pricing
# Fill in with the right prices
PRICES = {
    "anthropic/claude-haiku-4.5": {"input": 0.80, "output": 4.00},
    "anthropic/claude-sonnet-5.5": {"input": 3.00, "output": 15.00},
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
    price = PRICES[model]
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


def main():
    model = "anthropic/claude-haiku-4.5"

    # Estimate: count words and multiply by ~1.3 for tokens
    estimated_input_tokens = len(PROMPT.split()) * 1.3
    estimated_input_cost = cost_usd(model, int(estimated_input_tokens), 0)
    estimated_output_cost = cost_usd(model, 0, MAX_TOKENS)

    logger.info(f"used model: {model}")

    logger.info(f"Estimated input cost: ${estimated_input_cost:.6f}")
    logger.info(f"Estimated output cost (max): ${estimated_output_cost:.6f}")
    logger.info(f"Estimated total cost: ${estimated_input_cost + estimated_output_cost:.6f}")

    # Actual cost
    response = client.messages.create(model=model, max_tokens=MAX_TOKENS, messages=messages)

    actual_input_cost = cost_usd(model, response.usage.input_tokens, 0)
    actual_output_cost = cost_usd(model, 0, response.usage.output_tokens)

    logger.info(f"Actual input tokens: {response.usage.input_tokens}, cost: ${actual_input_cost:.6f}")
    logger.info(f"Actual output tokens: {response.usage.output_tokens}, cost: ${actual_output_cost:.6f}")
    logger.info(f"Actual total cost: ${actual_input_cost + actual_output_cost:.6f}")


if __name__ == "__main__":
    main()
