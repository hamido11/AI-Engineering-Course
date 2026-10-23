"""E3 - context-window stress test (needle in a haystack, lite)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from common.llm import ask

NEEDLE = "The access code is 7431."
FILLER = ("Operational note: systems nominal. " * 40 + "\n")


if __name__ == "__main__":
    for pages in (1, 5, 20, 60):
        doc = FILLER * pages
        body = doc[: len(doc) // 2] + NEEDLE + "\n" + doc[len(doc) // 2:]
        out = ask([{"role": "user",
                    "content": f"<doc>\n{body}\n</doc>\nWhat is the access code? Answer with the number only."}])
        print(f"{pages:3d} filler pages -> {out!r}")
