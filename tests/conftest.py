"""Offline test harness: a fake OpenAI client, so no API key or network is needed."""
import hashlib
import importlib.util
import math
import os
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "sk-test-not-real")
REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "labs" / "07-rag"))      # so `import rag` is one shared module

import common.llm as llm  # noqa: E402


def load_lab(relpath):
    """Import a lab script by path (folder names like '08-function-calling' aren't importable)."""
    path = REPO / relpath
    name = "lab_" + re.sub(r"\W", "_", relpath)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def fake_embedding(text, dims=128):
    """Deterministic bag-of-words embedding: texts sharing words land close together."""
    vec = [0.0] * dims
    for tok in re.findall(r"[a-z0-9\-]+", text.lower()):
        tok = tok.rstrip("s")
        vec[int(hashlib.md5(tok.encode()).hexdigest(), 16) % dims] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


class FakeClient:
    """Mimics the slices of the OpenAI client the labs use."""

    def __init__(self, reply="OK", chat_fn=None):
        self.calls = []
        self.reply = reply
        self.chat_fn = chat_fn
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._chat))
        self.embeddings = SimpleNamespace(create=self._embed)

    def _chat(self, **kw):
        self.calls.append(kw)
        if self.chat_fn:
            return self.chat_fn(**kw)
        msg = SimpleNamespace(content=self.reply, tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)],
                               usage=SimpleNamespace(prompt_tokens=10, completion_tokens=5))

    def _embed(self, model, input):
        return SimpleNamespace(data=[SimpleNamespace(embedding=fake_embedding(t)) for t in input])


@pytest.fixture(autouse=True)
def fake_llm(tmp_path, monkeypatch):
    monkeypatch.setenv("LEDGER_PATH", str(tmp_path / "ledger.csv"))
    monkeypatch.delenv("PRICE_IN_PER_M", raising=False)
    monkeypatch.delenv("PRICE_OUT_PER_M", raising=False)
    monkeypatch.delenv("CHAOS", raising=False)
    client = FakeClient()
    monkeypatch.setattr(llm, "_client", client)
    monkeypatch.setattr(llm, "_tokens_used", 0)
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)      # make backoff instant
    return client


@pytest.fixture
def lab():
    return load_lab
