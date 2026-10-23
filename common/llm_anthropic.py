"""Standalone Claude + Voyage port of the Lab-04 helper (common/llm.py).

This is a REFERENCE module, not wired into the labs. It mirrors the public shape of
common/llm.py -- ask(), embed(), a cost ledger, env-driven config, nothing hardcoded --
but talks to Anthropic for chat and Voyage AI for embeddings (Claude has no embeddings API).

To run the whole course on it, you would `from common import llm_anthropic as llm`
in a lab. Two shapes differ from the OpenAI version, on purpose (see NOTES at the bottom):
tool calls use Anthropic's native block format, and the system prompt is a separate arg.

Install:
    pip install anthropic voyageai        # (or add them to requirements.txt)

Configure (all via environment / .env, nothing hardcoded):
    ANTHROPIC_API_KEY   chat credential   (or run `ant auth login`; see NOTES)
    VOYAGE_API_KEY      embedding credential
    CHAT_MODEL          chat model id        (default: claude-opus-5-5 -> pick a current id)
    EMBED_MODEL         Voyage model id      (default: voyage-4; voyage-4-large = higher quality)
    JUDGE_MODEL         grader model, Lab 12 (default: same as CHAT_MODEL)
    EFFORT              low|medium|high|xhigh|max (optional; lower = cheaper on simple calls)
    PRICE_IN_PER_M      $ per 1M chat input tokens   (optional; ledger shows $0 until set)
    PRICE_OUT_PER_M     $ per 1M chat output tokens  (optional)
    PRICE_EMBED_PER_M   $ per 1M embedding tokens     (optional)
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
CHAT_MODEL = os.getenv("CHAT_MODEL", "claude-opus-5-5")
EMBED_MODEL = os.getenv("EMBED_MODEL", "voyage-4")
JUDGE_MODEL = os.getenv("JUDGE_MODEL", CHAT_MODEL)
EFFORT = os.getenv("EFFORT")                 # None -> let the model use its default

_client = None          # Anthropic client (tests/callers can inject a fake here)
_voyage = None          # Voyage client
_tokens_used = 0        # cumulative in+out tokens this process (agent budgets read it)


def get_client():
    """Create the Anthropic client lazily so importing this module never needs a key.
    Zero-arg constructor resolves ANTHROPIC_API_KEY, then ANTHROPIC_AUTH_TOKEN, then an
    `ant auth login` profile -- an unset env var does not mean 'no credentials'."""
    global _client
    if _client is None:
        import anthropic
        _client = anthropic.Anthropic(max_retries=4)   # SDK does the exponential backoff
    return _client


def get_voyage():
    """Lazy Voyage client; reads VOYAGE_API_KEY from the environment."""
    global _voyage
    if _voyage is None:
        import voyageai
        _voyage = voyageai.Client()
    return _voyage


def __getattr__(name):            # lets `from common.llm_anthropic import client` keep working
    if name == "client":
        return get_client()
    raise AttributeError(name)


def ledger_path() -> Path:
    return Path(os.getenv("LEDGER_PATH", ROOT / "cost_ledger.csv"))


def tokens_used() -> int:
    return _tokens_used


def _log_cost(model, tokens_in, tokens_out, price_in_env="PRICE_IN_PER_M",
              price_out_env="PRICE_OUT_PER_M"):
    """Append one row to the shared ledger CSV. Same schema as common/llm.py."""
    global _tokens_used
    _tokens_used += tokens_in + tokens_out
    price_in = float(os.getenv(price_in_env, "0") or 0)
    price_out = float(os.getenv(price_out_env, "0") or 0)
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


def _split_system(messages):
    """Anthropic takes the system prompt as a separate top-level arg, not a message.
    Pull any role='system' entries out of an OpenAI-style list and join them."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    convo = [m for m in messages if m["role"] != "system"]
    return (system or None), convo


def _text(message):
    """Concatenate the text blocks of an Anthropic response (skips thinking/tool_use)."""
    return "".join(b.text for b in message.content if b.type == "text")


def _usage(message):
    u = message.usage
    # Cache tokens (u.cache_read_input_tokens / u.cache_creation_input_tokens) also exist;
    # the course ledger only tracks plain in/out, so we keep parity.
    _log_cost(message.model, u.input_tokens, u.output_tokens)


def _stream(client, kwargs):
    parts = []
    with client.messages.stream(**kwargs) as stream:
        for piece in stream.text_stream:
            parts.append(piece)
            sys.stdout.write(piece)
            sys.stdout.flush()
        final = stream.get_final_message()
    print()
    _usage(final)
    if final.stop_reason == "refusal":
        return _refusal(final)
    return "".join(parts)


def _refusal(message):
    cat = getattr(message.stop_details, "category", None) if message.stop_details else None
    return f"[refused by safety policy{f': {cat}' if cat else ''}]"


def ask(messages, model=None, temperature=None, stream=False, tools=None,
        max_tokens=4096):
    """Single entry point: Claude Messages API with a cost ledger and optional streaming.

    Returns the text, or (when `tools` is given) the full Message so callers can read its
    `tool_use` blocks. Unlike the OpenAI wrapper, retries/backoff are handled by the SDK
    (max_retries on the client), so there is no hand-rolled loop here.

    `temperature` defaults to None: current Claude models (e.g. Opus 5.5) run thinking and
    reject a custom temperature with a 400. If you pass one and hit that, we retry once
    without it -- same spirit as the OpenAI wrapper.
    """
    import anthropic
    client = get_client()
    system, convo = _split_system(messages)

    while True:
        kwargs = {"model": model or CHAT_MODEL, "max_tokens": max_tokens, "messages": convo}
        if system:
            kwargs["system"] = system
        if EFFORT:
            kwargs["output_config"] = {"effort": EFFORT}
        if temperature is not None:
            kwargs["temperature"] = temperature
        if tools:
            kwargs["tools"] = tools
        try:
            if stream and not tools:
                return _stream(client, kwargs)
            resp = client.messages.create(**kwargs)
            _usage(resp)
            if resp.stop_reason == "refusal":
                return resp if tools else _refusal(resp)
            return resp if tools else _text(resp)
        except anthropic.BadRequestError as e:
            if temperature is not None and "temperature" in str(e).lower():
                temperature = None                      # retry once without it
                continue
            raise


def embed(texts, model=None, input_type=None):
    """Embed a list of strings -> list of vectors, via Voyage AI.

    Pass input_type='document' when indexing a corpus and input_type='query' when
    embedding a search query: Voyage encodes each side differently and retrieval improves.
    (The OpenAI wrapper had no such knob -- this is a small, real upgrade.)
    """
    result = get_voyage().embed(list(texts), model=model or EMBED_MODEL, input_type=input_type)
    _log_cost(model or EMBED_MODEL, result.total_tokens, 0,
              price_in_env="PRICE_EMBED_PER_M", price_out_env="PRICE_EMBED_PER_M")
    return result.embeddings


if __name__ == "__main__":
    # Small smoke test. Needs ANTHROPIC_API_KEY (and VOYAGE_API_KEY for the embed demo).
    print("chat >", end=" ")
    reply = ask([{"role": "system", "content": "You are a concise engineering assistant."},
                 {"role": "user", "content": "Explain embeddings in one sentence."}],
                stream=True)

    try:
        import math
        docs = ["Refunds take 3-5 business days.", "Physical goods ship in 2 business days."]
        dv = embed(docs, input_type="document")
        qv = embed(["how long until my money is back?"], input_type="query")[0]

        def cos(a, b):
            dot = sum(x * y for x, y in zip(a, b))
            na = math.sqrt(sum(x * x for x in a)) or 1.0
            nb = math.sqrt(sum(y * y for y in b)) or 1.0
            return dot / (na * nb)

        print("\nembed demo (query vs each doc):")
        for d, v in zip(docs, dv):
            print(f"  {cos(qv, v):.3f}  {d}")
    except Exception as e:
        print(f"\n[embed demo skipped: {e}]")

# ---------------------------------------------------------------------------
# NOTES -- what differs from common/llm.py, if you ever wire this into the labs
#
# 1. System prompt: Anthropic takes it as a top-level `system=` arg. ask() handles the
#    labs' OpenAI-style [{"role":"system",...}, ...] lists by pulling those out (_split_system).
#
# 2. Tool calling (labs 08, 10): Claude's shape is different end-to-end, so those labs
#    need adapting, not just an import swap:
#      - tool DEFS:   {"name","description","input_schema"}   (no {"type":"function",...} wrapper)
#      - tool CALLS:  come back as `tool_use` content blocks -> block.id / block.name / block.input
#                     (block.input is already a dict -- no json.loads needed, unlike OpenAI)
#      - tool RESULT: send back a user message with a `tool_result` block:
#                     {"role":"user","content":[{"type":"tool_result","tool_use_id":id,"content":...}]}
#      - forced tool_choice {"type":"any"|"tool"} is rejected (400) on Opus 5.5 / Sonnet 5.5;
#        use {"type":"auto"} + strict:true, or structured outputs.
#    LangGraph (lab 11): swap ChatOpenAI for `langchain_anthropic.ChatAnthropic` (pip install
#    langchain-anthropic) -- the graph itself is unchanged.
#
# 3. Embeddings are a different provider and model, so the vectors are not comparable to the
#    OpenAI index. Rebuild it: EMBED_MODEL=voyage-4 python labs/06-vector-db/reindex.py
#    (and reindex.py stamps embed_model into metadata, so old/new chunks won't be mixed).
#
# 4. Auth: if ANTHROPIC_API_KEY is unset, the zero-arg client still works after `ant auth login`.
#
# 5. Refusals: Opus 5.5 can stop with stop_reason='refusal' (returned here as a readable
#    string). For automatic recovery, Anthropic offers server-side `fallbacks` (beta).
# ---------------------------------------------------------------------------
