"""E1-E4 - bounded agent loop: iteration, token and wall-clock caps; loud failure;
reflection; human gate on writes."""
import json
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from common.llm import ask, tokens_used

SANDBOX = (Path(__file__).resolve().parent / "sandbox").resolve()   # the only writable directory
SANDBOX.mkdir(exist_ok=True)

TOOLS = [
    {"type": "function", "function": {"name": "list_files",
        "description": "List files in the sandbox.", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "read_file",
        "description": "Read a sandbox file.", "parameters": {"type": "object",
        "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {"name": "write_file",
        "description": "Write a sandbox file. Requires human approval.", "parameters": {"type": "object",
        "properties": {"name": {"type": "string"}, "content": {"type": "string"}}, "required": ["name", "content"]}}},
]


def safe(name):
    """Resolve inside the sandbox or refuse. (A string-prefix check is NOT enough:
    'sandbox_evil/x' starts with 'sandbox'. Compare resolved paths instead.)"""
    p = (SANDBOX / name).resolve()
    if not p.is_relative_to(SANDBOX):
        raise ValueError("path escape blocked")
    return p


def run_tool(name, args):
    if name == "list_files":
        return sorted(p.name for p in SANDBOX.iterdir())
    if name == "read_file":
        return safe(args["name"]).read_text()[:2000]
    if name == "write_file":                                  # E4: human gate
        target = safe(args["name"])
        print(f"\n[GATE] write {args['name']!r} ({len(args['content'])} chars). Preview:")
        print(args["content"][:200])
        if input("approve? y/n: ").lower() != "y":
            return {"error": "write rejected by human"}
        target.write_text(args["content"])
        return {"written": args["name"]}
    return {"error": f"no such tool {name!r}"}


def run_agent(goal, max_iters=8, budget_s=60, max_tokens=20_000):
    """Three independent caps (E1). Any of them stops the run with a loud FAILED."""
    t0, tok0 = time.time(), tokens_used()
    msgs = [{"role": "system", "content":
             "You are a careful agent. Before each action, critique your previous step in one sentence. "
             "When the goal is complete, reply DONE: <summary>. If impossible, reply FAILED: <why>."},
            {"role": "user", "content": goal}]
    for i in range(max_iters):
        if time.time() - t0 > budget_s:
            return f"FAILED: wall-clock budget ({budget_s}s) exhausted at step {i}"
        if tokens_used() - tok0 > max_tokens:
            return f"FAILED: token budget ({max_tokens}) exhausted at step {i}"
        msg = ask(msgs, tools=TOOLS)
        if not msg.tool_calls:
            return msg.content                       # DONE or FAILED, model-declared
        msgs.append(msg)
        for tc in msg.tool_calls:
            try:
                result = run_tool(tc.function.name, json.loads(tc.function.arguments))
            except Exception as e:
                result = {"error": str(e)}
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return f"FAILED: max_iters ({max_iters}) reached without completion"


if __name__ == "__main__":
    print(run_agent("Organize the sandbox: propose a naming scheme for its files, "
                    "then write a PLAN.md describing the moves (do not move anything)."))
