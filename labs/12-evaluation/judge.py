"""E3 - LLM-as-judge with a written rubric; calibrate against your own labels."""
import re
import sys
from pathlib import Path
REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))                         # `common`
sys.path.insert(0, str(REPO / "labs" / "07-rag"))     # `rag`
from common.llm import JUDGE_MODEL, ask

RUBRIC = """Score the ANSWER for the QUESTION on 1-5:
5 = fully correct, grounded, cites context; 3 = partially correct or uncited; 1 = wrong or hallucinated.
Reply with the integer only."""


def parse_score(text):
    m = re.search(r"[1-5]", text)
    if not m:
        raise ValueError(f"judge returned no 1-5 score: {text!r}")
    return int(m.group())


def judge(question, answer_text, model=None):
    out = ask([{"role": "system", "content": RUBRIC},
               {"role": "user", "content": f"QUESTION: {question}\nANSWER: {answer_text}"}],
              model=model or JUDGE_MODEL, temperature=0)
    return parse_score(out)

# Calibration: judge 5 outputs, score the same 5 yourself.
# Mean absolute disagreement > 1.0 means the rubric (not you) needs fixing.
