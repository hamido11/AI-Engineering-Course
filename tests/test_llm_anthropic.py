"""Offline tests for the standalone Claude + Voyage port (common/llm_anthropic.py).

Mirrors tests/test_llm.py, but against fake Anthropic / Voyage clients so no key or
network is needed. The whole module is skipped unless both SDKs are installed
(same convention as the mcp test), so it never breaks a minimal install."""
import csv
from types import SimpleNamespace

import pytest

anthropic = pytest.importorskip("anthropic")
pytest.importorskip("voyageai")

import common.llm_anthropic as la  # noqa: E402


# ---------- fakes ----------
def message(text="OK", in_tok=10, out_tok=5, model="claude-test",
            stop_reason="end_turn", stop_details=None, content=None):
    """Mimic the slice of an Anthropic Message the port reads."""
    if content is None:
        content = [SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(
        content=content, model=model, stop_reason=stop_reason, stop_details=stop_details,
        usage=SimpleNamespace(input_tokens=in_tok, output_tokens=out_tok))


class FakeStream:
    def __init__(self, pieces, final):
        self.text_stream = pieces
        self._final = final

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get_final_message(self):
        return self._final


class FakeAnthropic:
    def __init__(self, create_fn=None, stream=None):
        self.calls = []
        self._create_fn = create_fn
        self._stream = stream
        self.messages = SimpleNamespace(create=self._create, stream=self._stream_cm)

    def _create(self, **kw):
        self.calls.append(kw)
        return self._create_fn(**kw) if self._create_fn else message()

    def _stream_cm(self, **kw):
        self.calls.append(kw)
        return self._stream


class FakeVoyage:
    def embed(self, texts, model=None, input_type=None):
        texts = list(texts)
        self.last = {"texts": texts, "model": model, "input_type": input_type}
        vecs = [[float(len(t))] * 4 for t in texts]            # 4-dim toy vectors
        return SimpleNamespace(embeddings=vecs, total_tokens=sum(len(t) for t in texts))


@pytest.fixture
def anth(monkeypatch):
    """Inject a fake Anthropic client and give each test a clean token counter."""
    monkeypatch.setattr(la, "_tokens_used", 0)

    def install(client):
        monkeypatch.setattr(la, "_client", client)
        return client
    return install


@pytest.fixture
def voy(monkeypatch):
    v = FakeVoyage()
    monkeypatch.setattr(la, "_voyage", v)
    monkeypatch.setattr(la, "_tokens_used", 0)
    return v


# ---------- ask() ----------
def test_ask_returns_text_splits_system_and_omits_optional_args(anth):
    client = anth(FakeAnthropic(create_fn=lambda **kw: message("hello world")))
    out = la.ask([{"role": "system", "content": "be nice"},
                  {"role": "user", "content": "hi"}])
    assert out == "hello world"
    kw = client.calls[-1]
    assert kw["system"] == "be nice"                       # system pulled into its own arg
    assert kw["messages"] == [{"role": "user", "content": "hi"}]
    assert kw["model"] == la.CHAT_MODEL and "max_tokens" in kw
    assert "temperature" not in kw                          # not sent by default (Claude 400s on it)
    assert "output_config" not in kw                        # no EFFORT set -> model default


def test_split_system_joins_multiple_and_keeps_order():
    system, convo = la._split_system([
        {"role": "system", "content": "a"},
        {"role": "user", "content": "u"},
        {"role": "system", "content": "b"},
        {"role": "assistant", "content": "x"}])
    assert system == "a\n\nb"
    assert convo == [{"role": "user", "content": "u"}, {"role": "assistant", "content": "x"}]


def test_ledger_and_token_counter(anth, monkeypatch):
    monkeypatch.setenv("PRICE_IN_PER_M", "1.0")
    monkeypatch.setenv("PRICE_OUT_PER_M", "2.0")
    anth(FakeAnthropic(create_fn=lambda **kw: message("x", in_tok=100, out_tok=50, model="m-test")))
    la.ask([{"role": "user", "content": "hi"}])
    rows = list(csv.DictReader(open(la.ledger_path())))
    assert rows[0]["model"] == "m-test" and rows[0]["tokens_in"] == "100"
    assert float(rows[0]["usd"]) == pytest.approx(100 / 1e6 * 1.0 + 50 / 1e6 * 2.0)
    assert la.tokens_used() == 150


def test_temperature_400_retries_without_it(anth):
    import httpx2
    seen = []

    def picky(**kw):
        seen.append(dict(kw))
        if "temperature" in kw:
            resp = httpx2.Response(400, request=httpx2.Request("POST", "https://api.anthropic.com/v1/messages"))
            raise anthropic.BadRequestError("Unsupported value: 'temperature'", response=resp, body=None)
        return message("fine")

    anth(FakeAnthropic(create_fn=picky))
    assert la.ask([{"role": "user", "content": "hi"}], temperature=0.2) == "fine"
    assert "temperature" in seen[0] and "temperature" not in seen[1]


def test_effort_env_sets_output_config(anth, monkeypatch):
    monkeypatch.setattr(la, "EFFORT", "low")
    client = anth(FakeAnthropic())
    la.ask([{"role": "user", "content": "hi"}])
    assert client.calls[-1]["output_config"] == {"effort": "low"}


def test_streaming_concatenates_and_logs_usage(anth, capsys):
    client = FakeAnthropic(stream=FakeStream(["Hel", "lo"], message("Hello", in_tok=7, out_tok=3)))
    anth(client)
    assert la.ask([{"role": "user", "content": "hi"}], stream=True) == "Hello"
    assert "Hello" in capsys.readouterr().out
    assert la.tokens_used() == 10


def test_refusal_is_surfaced(anth):
    sd = SimpleNamespace(category="cyber")
    anth(FakeAnthropic(create_fn=lambda **kw: message(stop_reason="refusal", stop_details=sd, content=[])))
    out = la.ask([{"role": "user", "content": "do a bad thing"}])
    assert "refused" in out.lower() and "cyber" in out


def test_tools_return_full_message_not_text(anth):
    tool_use = SimpleNamespace(type="tool_use", name="get_x", input={"a": 1}, id="t1")
    m = message(content=[tool_use], stop_reason="tool_use")
    client = anth(FakeAnthropic(create_fn=lambda **kw: m))
    out = la.ask([{"role": "user", "content": "hi"}],
                 tools=[{"name": "get_x", "description": "d", "input_schema": {"type": "object"}}])
    assert out is m                                         # caller gets the Message to read tool_use blocks
    assert client.calls[-1]["tools"]


# ---------- embed() ----------
def test_embed_passes_input_type_and_logs_tokens(voy, monkeypatch):
    monkeypatch.setenv("PRICE_EMBED_PER_M", "1.0")
    vecs = la.embed(["alpha", "beta gamma"], input_type="document")
    assert len(vecs) == 2 and len(vecs[0]) == 4
    assert voy.last["input_type"] == "document" and voy.last["model"] == la.EMBED_MODEL
    rows = list(csv.DictReader(open(la.ledger_path())))
    assert rows[0]["model"] == la.EMBED_MODEL and rows[0]["tokens_in"] == "15"   # 5 + 10 chars
