import csv
import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from loguru import logger

MODEL = "anthropic/claude-haiku-4.5"
# MODEL = "anthropic/claude-sonnet-5.5"
DATA = Path(__file__).resolve().parents[3] / "docs" / "session1"
OUTPUT_FILE = Path(__file__).parent / "prompting_patterns.csv"
ITEMS_PER_TASK = 2  # 3 tasks x 3 patterns x 2 items = 18 requests, under the 20 requests/minute limit

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise SystemExit("OPENROUTER_API_KEY is not set (check your .env file)")

client = anthropic.Anthropic(
    base_url="https://openrouter.ai/api",
    auth_token=OPENROUTER_API_KEY,
)


def ask(prompt, system=None, max_tokens=300):
    """Send one prompt. Returns (reply text, input tokens, output tokens)."""
    kwargs = {"system": system} if system else {}
    response = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    # The reply can start with a thinking block, which has no .text: keep only the text blocks
    text = "".join(block.text for block in response.content if block.type == "text")
    return text, response.usage.input_tokens, response.usage.output_tokens


def load(name):
    return json.loads((DATA / f"{name}.json").read_text(encoding="utf-8"))


CLS, ARI, STY = load("classification"), load("arithmetic"), load("style")
ONLY = "Reply with the answer only."
COT = "Think step by step, then end with a line 'Final answer: <answer>'."


def shots(examples, template):
    return "\n\n".join(template.format(**e) for e in examples)


# task -> (data, max_tokens, {pattern: item -> (system prompt, user prompt)})
TASKS = {
    "classification": (
        CLS,
        10,
        {
            "zero-shot": lambda i: (
                None,
                f"{CLS['instruction']}\n\nMessage: {i['input']}",
            ),
            "few-shot": lambda i: (
                None,
                (
                    f"{CLS['instruction']}\n\n"
                    f"{shots(CLS['examples'], 'Message: {input}\nCategory: {label}')}\n\n"
                    f"Message: {i['input']}\nCategory:"
                ),
            ),
            "system": lambda i: (
                f"{CLS['instruction']}\n\nRules: {CLS['rules']}",
                f"Message: {i['input']}",
            ),
        },
    ),
    "arithmetic": (
        ARI,
        1000,
        {
            "zero-shot": lambda i: (None, f"{i['question']}\n\n{ONLY}"),
            "few-shot": lambda i: (
                None,
                (
                    f"{ARI['instruction']} {ONLY}\n\n"
                    f"{shots(ARI['examples'], 'Problem: {question}\nAnswer: {answer}')}\n\n"
                    f"Problem: {i['question']}\nAnswer:"
                ),
            ),
            "chain of thought": lambda i: (None, f"{i['question']}\n\n{COT}"),
        },
    ),
    "style": (
        STY,
        60,
        {
            "zero-shot": lambda i: (
                None,
                f"{STY['instruction']} {ONLY}\n\nNotice: {i['input']}",
            ),
            "few-shot": lambda i: (
                None,
                (
                    f"{STY['instruction']} {ONLY}\n\n"
                    f"{shots(STY['examples'], 'Notice: {input}\nChalkboard: {output}')}\n\n"
                    f"Notice: {i['input']}\nChalkboard:"
                ),
            ),
            "system": lambda i: (
                f"{STY['instruction']}\n\nRules: {STY['rules']}\n{ONLY}",
                f"Notice: {i['input']}",
            ),
        },
    ),
}


def main():
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(
            [
                "task",
                "pattern",
                "item",
                "prompt",
                "expected",
                "answer",
                "tokens_in",
                "tokens_out",
            ]
        )
        for task, (data, max_tokens, patterns) in TASKS.items():
            for pattern, build in patterns.items():
                for item in data["items"][:ITEMS_PER_TASK]:
                    system, prompt = build(item)
                    text, tokens_in, tokens_out = ask(prompt, system, max_tokens)
                    expected = (
                        item.get("label") or item.get("answer") or ""
                    )  # style has no expected answer
                    logger.info(
                        "{} / {}: {!r} (expected {!r})",
                        task,
                        pattern,
                        text[-60:],
                        expected,
                    )
                    writer.writerow(
                        [
                            task,
                            pattern,
                            item.get("input") or item["question"],
                            f"{system}\n\n{prompt}" if system else prompt,
                            expected,
                            text,
                            tokens_in,
                            tokens_out,
                        ]
                    )
                    f.flush()  # keep the rows already written if a later request fails


if __name__ == "__main__":
    main()
