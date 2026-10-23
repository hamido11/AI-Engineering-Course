"""Ship-It - idempotent rebuild of the collection from source files.
Running it twice produces the identical index (ids are derived from content hashes)."""
import hashlib
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
import chromadb
from common.llm import embed, EMBED_MODEL

HERE = Path(__file__).resolve().parent
DOCS_DIR = HERE / "sample_docs"
PERSIST_PATH = HERE / ".chroma"
COLLECTION = "docs"


def load_chunks(docs_dir=DOCS_DIR):
    ids, docs, metas = [], [], []
    for path in sorted(Path(docs_dir).glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for i, para in enumerate(p for p in text.split("\n\n") if p.strip()):
            h = hashlib.sha256(para.encode()).hexdigest()[:16]
            ids.append(f"{path.name}:{i}:{h}")
            docs.append(para)
            metas.append({"source": path.name, "hash": h, "embed_model": EMBED_MODEL})
    return ids, docs, metas


def build_index(docs_dir=DOCS_DIR, persist_path=PERSIST_PATH, name=COLLECTION):
    """Wipe and rebuild the collection from source. The index is derived data."""
    db = chromadb.PersistentClient(path=str(persist_path))
    try:
        db.delete_collection(name)
    except Exception:
        pass                                   # first run: nothing to delete
    col = db.create_collection(name, metadata={"embed_model": EMBED_MODEL})
    ids, docs, metas = load_chunks(docs_dir)
    if not ids:
        raise SystemExit(f"no .md files found in {docs_dir}")
    col.add(ids=ids, documents=docs, metadatas=metas, embeddings=embed(docs))
    return col


if __name__ == "__main__":
    col = build_index()
    print(f"indexed {col.count()} chunks")

    # E1/E2: query with and without a metadata filter
    q = embed(["why did shipping fail with SHP-409"])[0]
    for label, where in (("no filter", None), ("source=shipping.md", {"source": "shipping.md"})):
        hits = col.query(query_embeddings=[q], n_results=2, where=where)
        print(f"\n[{label}]")
        for d in hits["documents"][0]:
            print("  hit:", d[:80].replace("\n", " "))
