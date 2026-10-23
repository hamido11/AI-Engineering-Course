"""Labs 05-07: chunking, a real Chroma index built with fake embeddings, retrieval, citations."""
import rag
from conftest import FakeClient


def build(tmp_path, lab):
    reindex = lab("labs/06-vector-db/reindex.py")
    col = reindex.build_index(persist_path=tmp_path / "chroma")
    rag.INDEX_PATH = tmp_path / "chroma"
    rag._col = None
    return reindex, col


def test_index_retrieves_the_right_document(tmp_path, lab):
    build(tmp_path, lab)
    refund = rag.retrieve("how long do refunds take after download", k=2)
    assert refund[0][0].startswith("refunds.md")
    ship = rag.retrieve("what does error SHP-409 mean", k=2)
    assert ship[0][0].startswith("shipping.md")


def test_reindex_is_idempotent(tmp_path, lab):
    reindex, col = build(tmp_path, lab)
    first, count = sorted(col.get()["ids"]), col.count()     # read BEFORE rebuilding: old handle dies
    col2 = reindex.build_index(persist_path=tmp_path / "chroma")
    assert sorted(col2.get()["ids"]) == first and col2.count() == count


def test_metadata_filter_changes_results(tmp_path, lab):
    _, col = build(tmp_path, lab)
    from conftest import fake_embedding
    q = fake_embedding("refund policy download")
    hits = col.query(query_embeddings=[q], n_results=5, where={"source": "shipping.md"})
    assert all(i.startswith("shipping.md") for i in hits["ids"][0])


def test_answer_puts_ids_in_context_and_refusal_in_system_prompt(tmp_path, lab, fake_llm):
    build(tmp_path, lab)
    fake_llm.reply = "Refunds take 3-5 business days [refunds.md:1]"
    text, ids = rag.answer_with_sources("how long do refunds take after download?", k=2)
    sent = fake_llm.calls[-1]["messages"]
    assert rag.REFUSAL in sent[0]["content"]
    assert f"[{ids[0]}]" in sent[1]["content"]
    assert "3-5 business days" in text


def test_missing_index_gives_a_helpful_error(tmp_path):
    import pytest
    rag.INDEX_PATH = tmp_path / "nothing-here"
    rag._col = None
    with pytest.raises(SystemExit, match="reindex"):
        rag.get_collection()


def test_chunkers(lab):
    ch = lab("labs/05-embeddings/chunkers.py")
    text = "para one.\n\n" + "x" * 500 + "\n\npara three."
    fixed = ch.fixed(text, size=100, overlap=10)
    assert all(len(c) <= 100 for c in fixed) and "".join(fixed)
    paras = ch.paragraphs(text, max_len=300)
    assert any("para one." in p for p in paras) and len(paras) >= 2


def test_semantic_grep_helpers(tmp_path, lab):
    sg = lab("labs/05-embeddings/semantic_grep.py")
    (tmp_path / "a.md").write_text("This paragraph is long enough to be kept as a chunk.\n\nshort")
    (tmp_path / "b.png").write_text("ignored")
    items = sg.chunks_from(tmp_path)
    assert len(items) == 1 and items[0][0] == "a.md"
    import numpy as np
    m = np.array([[1.0, 0.0], [0.0, 1.0]])
    sims = sg.cosine(m, np.array([1.0, 0.0]))
    assert sims[0] > sims[1]
