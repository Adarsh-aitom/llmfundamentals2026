"""
Compare LLMs from Anthropic and OpenAI on the same prompts, using your LLMWrapper.
"""
import csv
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

from src.common.llmwrapper import LLMWrapper

# (provider, model)
MODELS = [
    ("anthropic", "anthropic/claude-haiku-4.5"),
    ("anthropic", "anthropic/claude-sonnet-5.5"),
    ("openai", "openai/gpt-4.1-mini"),
    # TODO add one more model, from either provider
]
PROMPTS = [
    "Explain in two sentences what a balance sheet is.",
    "Write a short professional email asking a professor for an extension on a report.",
    "A company has 120 employees and 35% work remotely. How many work on site?",
]
OUTPUT_FILE = Path(__file__).parent / "comparing_llms.csv"

load_dotenv()  # reads the .env file


def main():
    rows = []
    for provider, model in MODELS:
        llm = LLMWrapper(provider, model=model)
        for prompt in PROMPTS:
            # TODO ask the model with your wrapper
            response = ...
            logger.info("{} | {!r}: {}", model, prompt, response)
            # TODO add a row: model, prompt, answer, tokens, cost, latency
            rows.append([])

    # TODO save the rows to OUTPUT_FILE (csv, sep=";") with a header

    # TODO log one line per model: average cost and average latency
    # Which model is the cheapest? The fastest? Is the answer of the cheapest one good enough?


if __name__ == "__main__":
    main()
