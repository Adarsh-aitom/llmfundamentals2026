import os

import anthropic
from dotenv import load_dotenv
from loguru import logger

MODEL = "anthropic/claude-haiku-4.5"
MAX_TOKENS = 100
# PROMPT = "Describe winter in one poetic sentence.""
PROMPT = "What cartoon character would make the best president?"
TEMPERATURES = [0.0, 0.5, 1.0]
TOP_PS = [0.1, 0.5, 1.0]

load_dotenv()  # reads the .env file
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY is not set (check your .env file)")

client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api",
    auth_token=OPENROUTER_API_KEY,
)


def ask(prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"temperature": 0.5},  # or {"top_p": 0.9}, not both
    )
    return response.content[0].text


def main():
    # TODO change temperature
    logger.info(ask(PROMPT))

    # TODO change top p


if __name__ == "__main__":
    main()
