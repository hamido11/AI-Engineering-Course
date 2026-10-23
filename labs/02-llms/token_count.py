"""E1 - count tokens and predict cost. Set PRICE_IN_PER_M in .env from your provider's pricing page."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
import os
import tiktoken

ROOT = Path(__file__).resolve().parents[2]
PRICE_IN_PER_M = float(os.getenv("PRICE_IN_PER_M", "0") or 0)


if __name__ == "__main__":

    enc = tiktoken.get_encoding("o200k_base")
    samples = {
        "tweet": "Shipped the RAG bot today. Retrieval quality was the whole game.",
        "prose_page": (ROOT / "README.md").read_text(encoding="utf-8"),
        "code_file": (ROOT / "common" / "llm.py").read_text(encoding="utf-8"),
    }
    for name, text in samples.items():
        n = len(enc.encode(text))
        cost = n / 1e6 * PRICE_IN_PER_M
        note = f"~${cost:.6f} as input" if PRICE_IN_PER_M else "(set PRICE_IN_PER_M to see cost)"
        print(f"{name:12s} {n:6d} tokens  {note}")
