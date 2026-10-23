"""E2 - same prompt, three temperatures, three samples each.
Note: some newer models ignore or reject custom temperature; ask() retries without it."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from common.llm import ask

PROMPT = [{"role": "user", "content": "Name a plausible startup that sells embeddings-as-a-service. One name only."}]


if __name__ == "__main__":
    for t in (0.0, 0.7, 1.2):
        outs = [ask(PROMPT, temperature=t) for _ in range(3)]
        print(f"T={t}: {outs}")
    print("\nDecide: which setting does YOUR project need, and why?")
