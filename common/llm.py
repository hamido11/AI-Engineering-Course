"""Shared LLM helper: the deliverable of Lab 04, imported by every later lab.

Configuration (all via environment / .env, nothing hardcoded):
  CHAT_MODEL        chat model id        (default: gpt-4o-mini  -> set to a CURRENT model, see README)
  EMBED_MODEL       embedding model id   (default: text-embedding-3-small)
  JUDGE_MODEL       grader model, Lab 12 (default: same as CHAT_MODEL)
  PRICE_IN_PER_M    $ per 1M input tokens  (optional; ledger shows $0 until you set it)
  PRICE_OUT_PER_M   $ per 1M output tokens (optional)
"""
import csv
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", CHAT_MODEL)
TRANSIENT = (429, 500, 502, 503, 504)

_client = None          # tests inject a fake here
_tokens_used = 0        # cumulative in+out tokens this process (agent budgets read it)


def get_client():
    """Create the OpenAI client lazily so importing this module never needs a key."""
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI()
    return _client


def __getattr__(name):            # lets `from common.llm import client` keep working
    if name == "client":
        return get_client()
    raise AttributeError(name)


def ledger_path() -> Path:
    return Path(os.getenv("LEDGER_PATH", ROOT / "cost_ledger.csv"))


def tokens_used() -> int:
    return _tokens_used


def _log_cost(model, tokens_in, tokens_out):
    global _tokens_used
    _tokens_used += tokens_in + tokens_out
    price_in = float(os.getenv("PRICE_IN_PER_M", "0") or 0)
    price_out = float(os.getenv("PRICE_OUT_PER_M", "0") or 0)
    cost = tokens_in / 1e6 * price_in + tokens_out / 1e6 * price_out
    path = ledger_path()
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["ts", "model", "tokens_in", "tokens_out", "usd"])
        w.writerow([datetime.now(timezone.utc).isoformat(), model,
                    tokens_in, tokens_out, f"{cost:.6f}"])
    return cost


def _stream(client, kwargs, model):
    stream = client.chat.completions.create(
        **kwargs, stream=True, stream_options={"include_usage": True})
    parts, usage = [], None
    for chunk in stream:
        if getattr(chunk, "usage", None):
            usage = chunk.usage
        if chunk.choices and chunk.choices[0].delta.content:
            piece = chunk.choices[0].delta.content
            parts.append(piece)
            sys.stdout.write(piece)
            sys.stdout.flush()
    print()
    if usage:
        _log_cost(model, usage.prompt_tokens, usage.completion_tokens)
    return "".join(parts)


def ask(messages, model=None, temperature=0.2, stream=False, tools=None,
        max_retries=4):
    """Single entry point: retries with backoff, optional streaming, cost ledger.

    Returns the text, or (when `tools` is given) the full assistant message so
    callers can read `.tool_calls`. Streaming is ignored when tools are used.
    Some newer models reject a custom temperature; on that 400 we retry once
    without it instead of crashing.
    """
    model = model or CHAT_MODEL
    client = get_client()
    delay, attempt = 1.0, 0
    while True:
        try:
            kwargs = {"model": model, "messages": messages}
            if temperature is not None:
                kwargs["temperature"] = temperature
            if tools:
                kwargs["tools"] = tools
            if stream and not tools:
                return _stream(client, kwargs, model)
            resp = client.chat.completions.create(**kwargs)
            if resp.usage:
                _log_cost(model, resp.usage.prompt_tokens, resp.usage.completion_tokens)
            msg = resp.choices[0].message
            return msg if tools else msg.content
        except Exception as e:
            code = getattr(e, "status_code", None)
            if code == 400 and temperature is not None and "temperature" in str(e).lower():
                temperature = None
                continue
            if code in TRANSIENT and attempt < max_retries:
                time.sleep(delay)
                delay *= 2
                attempt += 1
                continue
            raise


def embed(texts, model=None):
    """Embed a list of strings -> list of vectors."""
    resp = get_client().embeddings.create(model=model or EMBED_MODEL, input=list(texts))
    return [d.embedding for d in resp.data]
