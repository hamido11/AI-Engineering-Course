"""E1/E2 - end-to-end RAG with citations and honest refusals.
Needs Lab 06's index first:  python ../06-vector-db/reindex.py"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
import chromadb
from common.llm import ask, embed

REPO = Path(__file__).resolve().parents[2]
INDEX_PATH = REPO / "labs" / "06-vector-db" / ".chroma"
REFUSAL = "I don't know based on the provided documents."

SYSTEM = f"""Answer ONLY from the provided context chunks.
Cite chunk ids in [brackets] after each claim.
If the context does not contain the answer, reply exactly: "{REFUSAL}"
"""

_col = None


def get_collection():
    global _col
    if _col is None:
        missing = "No index found. Run: python labs/06-vector-db/reindex.py"
        if not Path(INDEX_PATH).exists():          # don't let Chroma create an empty dir as a side effect
            raise SystemExit(missing)
        try:
            _col = chromadb.PersistentClient(path=str(INDEX_PATH)).get_collection("docs")
        except Exception:
            raise SystemExit(missing)
    return _col


def retrieve(question, k=4):
    """Return [(chunk_id, text), ...]. Also usable as an agent tool (Lab 11)."""
    hits = get_collection().query(query_embeddings=[embed([question])[0]], n_results=k)
    return list(zip(hits["ids"][0], hits["documents"][0]))


def answer_with_sources(question, k=4):
    """Return (answer_text, [chunk_ids_in_context]) so callers can verify citations."""
    chunks = retrieve(question, k)
    ctx = "\n\n".join(f"[{i}] {d}" for i, d in chunks)
    text = ask([{"role": "system", "content": SYSTEM},
                {"role": "user", "content": f"<context>\n{ctx}\n</context>\n\nQuestion: {question}"}])
    return text, [i for i, _ in chunks]


def answer(question, k=4):
    return answer_with_sources(question, k)[0]


if __name__ == "__main__":
    for q in ["How long do refunds take after download?",
              "What does SHP-409 mean?",
              "What is the CEO's salary?"]:          # must refuse
        print(f"\nQ: {q}\nA: {answer(q)}")
