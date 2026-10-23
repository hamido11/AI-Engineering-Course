"""E3 - prove the retry logic survives simulated 429s.
The first 3 calls are faked failures; the 4th is a real request, so this needs a valid key."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
import common.llm as llm


class Boom(Exception):
    status_code = 429


if __name__ == "__main__":
    calls = {"n": 0}
    client = llm.get_client()
    real = client.chat.completions.create

    def flaky(**kw):
        calls["n"] += 1
        if calls["n"] <= 3:
            raise Boom("simulated rate limit")
        return real(**kw)

    client.chat.completions.create = flaky
    out = llm.ask([{"role": "user", "content": "Say OK."}])
    print(f"survived {calls['n'] - 1} failures ->", out)
