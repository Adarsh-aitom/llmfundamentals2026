import csv
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from loguru import logger

MODELS = ["anthropic/claude-haiku-4.5", "anthropic/claude-sonnet-5.5"]
MAX_TOKENS = 10000
PROMPTS = [
    "Say hello in French.",
    "Explain in one sentence what a token is.",
    "Describe how a cat sees the world in one paragraph.",
    "Give advice about how to give engaging presentations in front of a large audience.",
]
OUTPUT_FILE = Path(__file__).parent / "estimating_costs.csv"

# Pricing page: https://platform.claude.com/docs/en/about-claude/pricing
# Prices in USD per million tokens
PRICES = {
    "anthropic/claude-haiku-4.5": {"input": 0.10, "output": 0.50},
    "anthropic/claude-sonnet-5.5": {"input": 2.00, "output": 10.00},
}

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY is not set (check your .env file)")

client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api",
    auth_token=OPENROUTER_API_KEY,
)


def cost_usd(model, input_tokens, output_tokens):
    price = PRICES[model]
    return (input_tokens * price["input"] + output_tokens * price["output"]) / 1_000_000


def main():
    rows = []
    for model in MODELS:
        for prompt in PROMPTS:
            response = client.messages.create(
                model=model,
                max_tokens=MAX_TOKENS,
                messages=[{"role": "user", "content": prompt}],
            )
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            actual_cost = cost_usd(model, input_tokens, output_tokens)
            answer = response.content[0].text

            logger.info(
                "{} {!r}: ${:.6f} ({} in, {} out)",
                model,
                prompt,
                actual_cost,
                input_tokens,
                output_tokens,
            )
            rows.append(
                [model, prompt, input_tokens, output_tokens, actual_cost, answer]
            )

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "model",
                "prompt",
                "input_tokens",
                "output_tokens",
                "actual_cost_usd",
                "answer",
            ]
        )
        writer.writerows(rows)


if __name__ == "__main__":
    main()
