import csv
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from loguru import logger

MODEL = "anthropic/claude-haiku-4.5"
MAX_TOKENS = 100

# PROMPT = "Describe winter in one poetic sentence."
PROMPT = "What cartoon character would make the best president?"
TEMPERATURES = [0.0, 0.5, 1.0]
TOP_PS = [0.1, 0.5, 1.0]
RUNS = 2  # requests per setting
OUTPUT_FILE = Path(__file__).parent / "temperature_and_top_p_exploration.csv"

load_dotenv()  # reads the .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY is not set (check your .env file)")

client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api",
    auth_token=OPENROUTER_API_KEY,
)


def ask(prompt, **sampling):
    """Send one prompt. sampling is e.g. temperature=0.5 (not together with top_p)."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
        extra_body=sampling,
    )
    return response.content[0].text


def main():
    settings = [{"temperature": t} for t in TEMPERATURES] + [
        {"top_p": p} for p in TOP_PS
    ]
    rows = []
    for sampling in settings:
        for _ in range(RUNS):
            answer = ask(PROMPT, **sampling)
            logger.info("{}: {}", sampling, answer)
            rows.append([PROMPT, sampling, answer])

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(["prompt", "extra_body", "answer"])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
