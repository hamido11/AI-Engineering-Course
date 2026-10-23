import csv
from types import SimpleNamespace

import pytest

import common.llm as llm
from conftest import FakeClient


class HttpError(Exception):
    def __init__(self, status_code, msg="boom"):
        super().__init__(msg)
        self.status_code = status_code


def ok_response(text="done"):
    msg = SimpleNamespace(content=text, tool_calls=None)
    return SimpleNamespace(choices=[SimpleNamespace(message=msg)],
                           usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50))


def test_retries_survive_three_429s(monkeypatch):
    n = {"calls": 0}

    def flaky(**kw):
        n["calls"] += 1
        if n["calls"] <= 3:
            raise HttpError(429)
        return ok_response("recovered")

    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=flaky))
    assert llm.ask([{"role": "user", "content": "hi"}]) == "recovered"
    assert n["calls"] == 4


def test_non_transient_errors_are_not_retried(monkeypatch):
    n = {"calls": 0}

    def bad(**kw):
        n["calls"] += 1
        raise HttpError(401, "invalid api key")

    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=bad))
    with pytest.raises(HttpError):
        llm.ask([{"role": "user", "content": "hi"}])
    assert n["calls"] == 1


def test_gives_up_after_max_retries(monkeypatch):
    n = {"calls": 0}

    def always_429(**kw):
        n["calls"] += 1
        raise HttpError(429)

    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=always_429))
    with pytest.raises(HttpError):
        llm.ask([{"role": "user", "content": "hi"}], max_retries=2)
    assert n["calls"] == 3          # first try + 2 retries


def test_temperature_rejection_retries_without_it(monkeypatch):
    seen = []

    def picky(**kw):
        seen.append(dict(kw))
        if "temperature" in kw:
            raise HttpError(400, "Unsupported value: 'temperature' does not support 0.2")
        return ok_response("fine")

    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=picky))
    assert llm.ask([{"role": "user", "content": "hi"}]) == "fine"
    assert "temperature" in seen[0] and "temperature" not in seen[1]


def test_ledger_and_token_counter(tmp_path, monkeypatch):
    monkeypatch.setenv("PRICE_IN_PER_M", "1.0")
    monkeypatch.setenv("PRICE_OUT_PER_M", "2.0")
    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=lambda **kw: ok_response()))
    llm.ask([{"role": "user", "content": "hi"}], model="m-test")
    rows = list(csv.DictReader(open(llm.ledger_path())))
    assert rows[0]["model"] == "m-test" and rows[0]["tokens_in"] == "100"
    assert float(rows[0]["usd"]) == pytest.approx(100 / 1e6 * 1.0 + 50 / 1e6 * 2.0)
    assert llm.tokens_used() == 150


def test_ledger_shows_zero_dollars_until_prices_are_set():
    llm.ask([{"role": "user", "content": "hi"}])
    assert float(list(csv.DictReader(open(llm.ledger_path())))[0]["usd"]) == 0.0


def test_tools_return_full_message_not_text(monkeypatch):
    msg = SimpleNamespace(content=None, tool_calls=[object()])
    resp = SimpleNamespace(choices=[SimpleNamespace(message=msg)],
                           usage=SimpleNamespace(prompt_tokens=1, completion_tokens=1))
    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=lambda **kw: resp))
    out = llm.ask([{"role": "user", "content": "hi"}], tools=[{"type": "function"}])
    assert out.tool_calls


def test_streaming_concatenates_and_logs_usage(monkeypatch, capsys):
    def chunk(text=None, usage=None):
        choices = [SimpleNamespace(delta=SimpleNamespace(content=text))] if text else []
        return SimpleNamespace(choices=choices, usage=usage)

    stream = [chunk("Hel"), chunk("lo"),
              chunk(usage=SimpleNamespace(prompt_tokens=7, completion_tokens=3))]
    monkeypatch.setattr(llm, "_client", FakeClient(chat_fn=lambda **kw: iter(stream)))
    assert llm.ask([{"role": "user", "content": "hi"}], stream=True) == "Hello"
    assert "Hello" in capsys.readouterr().out
    assert llm.tokens_used() == 10


def test_embed_returns_one_vector_per_text():
    vecs = llm.embed(["alpha", "beta gamma"])
    assert len(vecs) == 2 and len(vecs[0]) == 128
