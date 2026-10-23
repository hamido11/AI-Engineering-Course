"""Importing a lab script must never call an API, touch the network, or spend money.
(Regression: needle_test.py once ran at import time, so `pytest` collected it and hit the live API.)"""
from types import SimpleNamespace

import pytest

import common.llm as llm
from conftest import REPO, load_lab

SCRIPTS = sorted(p.relative_to(REPO).as_posix() for p in (REPO / "labs").rglob("*.py"))


def explode(*a, **k):
    raise AssertionError("API call attempted at import time")


@pytest.mark.parametrize("script", SCRIPTS)
def test_import_makes_no_api_call(script, monkeypatch):
    bomb = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=explode)),
                           embeddings=SimpleNamespace(create=explode))
    monkeypatch.setattr(llm, "_client", bomb)
    load_lab(script)


def test_no_lab_script_matches_pytest_collection_patterns():
    bad = [s for s in SCRIPTS if s.endswith("_test.py") or s.split("/")[-1].startswith("test_")]
    assert not bad, f"pytest would collect these live-API scripts: {bad}"


def test_llm_anthropic_import_creates_no_client():
    """The Claude port is import-safe too: importing it builds no client, so it needs no key."""
    import importlib

    import common.llm_anthropic as m
    importlib.reload(m)                      # re-run the module top level with a clean slate
    assert m._client is None and m._voyage is None
