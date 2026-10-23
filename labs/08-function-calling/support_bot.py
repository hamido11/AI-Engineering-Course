"""Ship-It - support bot: statuses auto-answered, refunds drafted but human-gated."""
import json
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from common.llm import ask

ORDERS = {"A1001": {"status": "shipped", "eta": "2026-08-12", "amount": 49.00},
          "A1002": {"status": "processing", "eta": None, "amount": 19.00}}
ORDER_ID = re.compile(r"^A[0-9]{4}$")

TOOLS = [
    {"type": "function", "function": {
        "name": "get_order_status",
        "description": "Look up shipping status of an order. Use ONLY when the user provides an order id like A1001.",
        "parameters": {"type": "object",
                       "properties": {"order_id": {"type": "string", "pattern": "^A[0-9]{4}$"}},
                       "required": ["order_id"]}}},
    {"type": "function", "function": {
        "name": "issue_refund",
        "description": "Draft a refund. DANGEROUS: requires human confirmation before execution.",
        "parameters": {"type": "object",
                       "properties": {"order_id": {"type": "string"}, "reason": {"type": "string"}},
                       "required": ["order_id", "reason"]}}},
]


def run_tool(name, args):
    """Model-produced arguments are untrusted input: validate before acting."""
    oid = args.get("order_id", "") if isinstance(args, dict) else ""
    if name in ("get_order_status", "issue_refund"):
        if not isinstance(oid, str) or not ORDER_ID.match(oid):
            return {"error": f"malformed order id {oid!r}; expected like A1001"}
        if oid not in ORDERS:
            return {"error": f"unknown order id {oid!r}; ask the user to double-check"}
    if name == "get_order_status":
        return ORDERS[oid]
    if name == "issue_refund":
        ok = input(f"\n[GATE] Refund ${ORDERS[oid]['amount']} on {oid}? type YES to approve: ")
        if ok.strip() != "YES":
            return {"error": "refund rejected by human reviewer"}
        return {"refunded": oid, "amount": ORDERS[oid]["amount"]}
    return {"error": f"no such tool {name!r}"}


def chat(user_msg, max_rounds=5):
    msgs = [{"role": "system", "content": "You are a support agent. Use tools when appropriate."},
            {"role": "user", "content": user_msg}]
    for _ in range(max_rounds):                       # bounded: never loop forever
        msg = ask(msgs, tools=TOOLS)
        if not msg.tool_calls:
            return msg.content
        msgs.append(msg)
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments)
            except json.JSONDecodeError:
                args = {}
            result = run_tool(tc.function.name, args)
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return "Sorry, I couldn't complete that request. A human agent will follow up."


if __name__ == "__main__":
    print(chat("Where is my order A1001?"))
    print(chat("Please refund order A1002, it arrived broken."))
