"""Ship-It - run the dataset against the Lab-07 pipeline; diff vs baseline; exit 1 on regression.

  python run_eval.py            # run, compare to baseline.json, update baseline if clean
Prereq: python ../06-vector-db/reindex.py
"""
import json
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))                         # `common`
sys.path.insert(0, str(REPO / "labs" / "07-rag"))     # `rag`

HERE = Path(__file__).resolve().parent
DATASET = HERE / "dataset.jsonl"
BASELINE = HERE / "baseline.json"
REFUSAL = "I don't know based on the provided documents."


def score(case, out):
    """Programmatic scorer: exact-ish refusal, or required substring."""
    checks = case["checks"]
    if checks.get("refusal"):
        return REFUSAL.lower() in out.lower()
    return checks["contains"].lower() in out.lower()


def load_cases(path=DATASET):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def regressions(baseline, results):
    """Cases that passed in the baseline but fail (or vanished) now."""
    return [k for k, was_ok in baseline.items() if was_ok and not results.get(k, False)]


def run(answer_fn, dataset=DATASET, baseline_path=BASELINE):
    results = {}
    for case in load_cases(dataset):
        results[case["id"]] = score(case, answer_fn(case["input"]))
        print(("PASS" if results[case["id"]] else "FAIL"), case["id"], "-", case["input"][:50])
    rate = sum(results.values()) / len(results)
    print(f"\npass rate: {rate:.0%}")
    baseline_path = Path(baseline_path)
    if baseline_path.exists():
        bad = regressions(json.loads(baseline_path.read_text()), results)
        if bad:
            print("REGRESSIONS vs baseline:", bad)
            return 1
    baseline_path.write_text(json.dumps(results, indent=1))
    print("baseline updated")
    return 0


if __name__ == "__main__":
    from rag import answer                               # the system under test
    sys.exit(run(answer))
