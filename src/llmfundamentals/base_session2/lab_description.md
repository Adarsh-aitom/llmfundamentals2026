# Session 2 lab — Build your LLM wrapper

## Goal

In session 1 you called one model with one script. In real applications you call several models, and
you need to know what each call costs, how long it takes, and what to do when it fails.

In this lab you build **`llmwrapper.py`**: a small class that hides the differences between Anthropic and
OpenAI, and adds the features you need for your application: cost, latency, retries, a cache and streaming.


## Before you start

- Your `.env` file contains your `OPENROUTER_API_KEY` (both providers go through OpenRouter). Don't forget to save the file once you've added the key.
- Install the OpenAI SDK if needed: `uv add openai`.
- Limit: a new OpenRouter account allows **20 requests per minute per model**. If you get a
  `RateLimitError`, wait one minute. Do not run a script in a loop.
- Work in `src/common/llmwrapper.py`.
- Pull the latest changes from the main repository.
- Create a branch for your session, for example with `git checkout -b session2`
- Once you're satisfied with your progress, commit your result with a message, for example `feat: added latency calculation`.

## Step 1 — Discover the pieces (the scripts of `base_session2/`)

Run each script, read the code, and write one sentence about what you saw.

| Script | Run | Question to answer |
|---|---|---|
| `0_api_connection_openai.py` | `uv run python src/llmfundamentals/base_session2/0_api_connection_openai.py` | What is different in the OpenAI response compared with the Anthropic one? |
| `1_latency.py` | same | Why is the second prompt slower than the first? |
| `2_cost.py` | same | Where do the token counts come from? Why is the cost known only after the call? |
| `3_streaming.py` | same | What do you see that you would not see without streaming? |
| `4_retry.py` | same | Which errors are retried, and which one is not? Why? |
| `5_cache.py` | same | What is different between the first and the second call? Why is the key a hash? |

## Step 2 — Build your own wrapper piece by piece

After each step, check it with the `__main__` block at
the bottom of your file (you can run it with `uv run python src/common/llmwrapper.py`).

1. Make LLMWrapper call either Anthropic or OpenAI. It is already set up for Anthropic, add it for OpenAi. [Optional] Reuse `0_api_connection_openai.py`.

2. **Latency.** Add `latency_seconds` to `LLMResponse`, measured around the whole `ask()`. [Optional] Reuse
   `1_latency.py`.

3. **Cost.** Add `cost_usd` to `LLMResponse` and a `PRICES_PER_MTOK` table. Reuse `2_cost.py`.


## [Optional] Step 3 - Add more features

4. **Streaming.** A `with_streaming` argument in `ask()`: a function that receives each piece of text as
   it arrives. Take `3_streaming.py` for Anthropic and write the OpenAI version yourself (the pieces are in
   `chunk.choices[0].delta.content`).

5. **Retries.** The decorator of `4_retry.py` around the method that sends the request, for both
   providers. The SDK clients must not retry by themselves (`max_retries=0`).

6. **Cache.** The SQLite cache of `5_cache.py`, checked at the start of `ask()`. The key must include
   everything that changes the answer: provider, model, `max_tokens`, system prompt and prompt. A cache hit
   costs `0.0`. Add `use_cache=True` to the constructor, so you can turn it off.
   *Check:* the second identical call is answered in a few milliseconds, with `cost_usd == 0.0`.


## Step 4 — Use your wrapper

Complete `5_comparing_llms.py` with your wrapper: ask the same prompts to several models from both
providers, and save the answers, token counts, cost and latency in a CSV file.

Then answer in the file (as a comment) or on paper:
- Which model is the cheapest? The fastest?
- Is the answer of the cheapest model good enough for each prompt?
- What would you choose for an application that answers customers in real time? And for one that
  summarises 10,000 documents overnight?


## Tips

- Run the `__main__` block after every step to check your work.
- If you are stuck on a step, read the matching script again: the code you need is almost there.
- Keep the methods short. If a method is longer than a screen, split it.
- Never put your API key in the code. It stays in `.env`.
