"""E1-E4 - the Lab-10 agent as a resumable LangGraph StateGraph.

  python graph_agent.py "What is the refund policy?"             # run
  python graph_agent.py "..." --approve                           # E4: pause before any tool runs
  python graph_agent.py --resume                                  # E3: continue after a kill/pause
Checkpoints persist in checkpoints.db, keyed by --thread.
"""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # repo root, so `common` imports from any cwd
from typing import Annotated
from typing_extensions import TypedDict

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "labs" / "07-rag"))
import rag                                                   # Lab 07 retriever
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode


@tool
def search_notes(query: str) -> str:
    """Search the knowledge index (Lab 07). Use for any question about policies or errors."""
    return "\n\n".join(f"[{i}] {t}" for i, t in rag.retrieve(query, k=4)) or "no results"


class State(TypedDict):
    messages: Annotated[list, add_messages]


def route(state: State):
    """E2: the branch decision is plain Python - unit-test it."""
    last = state["messages"][-1]
    return "tools" if getattr(last, "tool_calls", None) else END


def build_graph(llm=None):
    """Pass a fake llm in tests; by default builds the real OpenAI-backed one."""
    if llm is None:
        from langchain_openai import ChatOpenAI
        from common.llm import CHAT_MODEL
        llm = ChatOpenAI(model=CHAT_MODEL).bind_tools([search_notes])

    def agent(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    g = StateGraph(State)
    g.add_node("agent", agent)
    g.add_node("tools", ToolNode([search_notes]))
    g.add_edge(START, "agent")
    g.add_conditional_edges("agent", route, {"tools": "tools", END: END})
    g.add_edge("tools", "agent")
    return g


def main():
    from langgraph.checkpoint.sqlite import SqliteSaver
    ap = argparse.ArgumentParser()
    ap.add_argument("question", nargs="?")
    ap.add_argument("--thread", default="research-1")
    ap.add_argument("--resume", action="store_true", help="continue an interrupted run")
    ap.add_argument("--approve", action="store_true", help="pause for approval before tools run")
    a = ap.parse_args()
    if not a.resume and not a.question:
        ap.error("give a question, or use --resume")
    db = Path(__file__).resolve().parent / "checkpoints.db"
    with SqliteSaver.from_conn_string(str(db)) as saver:
        app = build_graph().compile(checkpointer=saver,
                                    interrupt_before=["tools"] if a.approve else None)
        cfg = {"configurable": {"thread_id": a.thread}}
        out = app.invoke(None if a.resume else {"messages": [("user", a.question)]}, cfg)
        while app.get_state(cfg).next:                       # paused before a node
            pending = app.get_state(cfg).values["messages"][-1].tool_calls
            print("PAUSED before tools:", [(c["name"], c["args"]) for c in pending])
            if input("approve? y/n: ").strip().lower() != "y":
                print("not approved; state saved, resume later with --resume")
                return
            out = app.invoke(None, cfg)
        print(out["messages"][-1].content)


if __name__ == "__main__":
    main()
