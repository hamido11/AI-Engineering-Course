"""E1/E2 - version tuple stamped on every answer + JSONL tracing + replay.

  python trace.py                 # ask one question, write a trace, print its id
  python trace.py <trace_id>      # replay that request against the CURRENT build
"""
import hashlib
import json
import time
import uuid
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))                         # `common`
sys.path.insert(0, str(REPO / "labs" / "07-rag"))     # `rag`
import rag
from common.llm import CHAT_MODEL, EMBED_MODEL

HERE = Path(__file__).resolve().parent
TRACES = HERE / "traces.jsonl"
DOCS_DIR = REPO / "labs" / "06-vector-db" / "sample_docs"
K = 4


def _h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:8]


def build_tuple():
    """Everything that can change an answer, pinned. Any answer must be reproducible from this."""
    docs = b"".join(p.read_bytes() for p in sorted(DOCS_DIR.glob("*.md")))
    cfg = json.dumps({"k": K, "embed": EMBED_MODEL}, sort_keys=True).encode()
    return {"model": CHAT_MODEL,
            "prompt": _h(rag.SYSTEM.encode()),
            "index": _h(docs),
            "config": _h(cfg)}


def traced_answer(q):
    t0, tid = time.time(), uuid.uuid4().hex[:8]
    out, ids = rag.answer_with_sources(q, K)
    rec = {"trace_id": tid, "ts": time.time(), "input": q, "output": out, "retrieved": ids,
           "latency_s": round(time.time() - t0, 3), "build": build_tuple()}
    with open(TRACES, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return out, tid


def find_trace(trace_id):
    if TRACES.exists():
        for line in TRACES.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec["trace_id"] == trace_id:
                return rec
    return None


def replay(trace_id):
    rec = find_trace(trace_id)
    if not rec:
        print("trace not found")
        return
    print("original build:", rec["build"], "\noriginal out:  ", rec["output"][:100])
    new, _ = traced_answer(rec["input"])
    print("current  build:", build_tuple(), "\ncurrent  out:  ", new[:100])
    changed = [k for k, v in rec["build"].items() if build_tuple()[k] != v]
    print("build drift in:", changed or "nothing (answer differences are model sampling)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        replay(sys.argv[1])
    else:
        out, tid = traced_answer("How long do refunds take after download?")
        print(out, f"\n[trace {tid}] replay with: python trace.py {tid}")
