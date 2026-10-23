"""Ship-It - streaming CLI chatbot with history, retries, and running cost.
The wrapper it exercises lives in common/llm.py (that's the real deliverable)."""
import csv
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from common.llm import ask, ledger_path

history = [{"role": "system", "content": "You are a concise engineering assistant."}]


def session_total():
    p = ledger_path()
    if not p.exists():
        return 0.0
    with open(p, newline="") as f:
        return sum(float(r["usd"]) for r in csv.DictReader(f))


if __name__ == "__main__":
    print("chat> Ctrl-C to exit")
    try:
        while True:
            user = input("\nyou > ").strip()
            if not user:
                continue
            history.append({"role": "user", "content": user})
            print("bot > ", end="")
            reply = ask(history, stream=True)
            history.append({"role": "assistant", "content": reply})
            print(f"      [ledger total so far: ${session_total():.4f}]")
    except (KeyboardInterrupt, EOFError):
        print("\nbye")
