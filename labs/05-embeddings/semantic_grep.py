"""Ship-It - semantic grep: query a folder by meaning, no vector DB.
Usage: python semantic_grep.py "how do refunds work" ./docs"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
import numpy as np
from common.llm import embed


def chunks_from(folder):
    out = []
    for root, _, files in os.walk(folder):
        for f in sorted(files):
            if f.endswith((".md", ".txt")):
                text = open(os.path.join(root, f), encoding="utf-8").read()
                for para in [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]:
                    out.append((f, para))
    return out


def cosine(matrix, vec):
    return matrix @ vec / (np.linalg.norm(matrix, axis=1) * np.linalg.norm(vec))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit('usage: python semantic_grep.py "your query" ./folder')
    query, folder = sys.argv[1], sys.argv[2]
    items = chunks_from(folder)
    if not items:
        sys.exit(f"no .md/.txt paragraphs found in {folder}")
    vecs = np.array(embed([t for _, t in items]))
    q = np.array(embed([query])[0])
    sims = cosine(vecs, q)
    for i in np.argsort(-sims)[:5]:
        f, para = items[i]
        print(f"[{sims[i]:.3f}] {f}: {para[:120]}...")
