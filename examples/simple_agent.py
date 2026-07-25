"""StateLens Example — Simple LangGraph Agent.

Demonstrates how to instrument a LangGraph application with StateLens.

Usage:
    pip install statelens-sdk[langgraph]
    python examples/simple_agent.py

Then run the StateLens server to view the results:
    statelens-server
    # Open http://localhost:8000/conversations
"""

from __future__ import annotations

import os
import sys

# Ensure the SDK is importable when running from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "sdk", "src"))

from statelens import observe

# --- LangGraph setup ---
# This example requires: pip install langgraph langchain-core langchain-openai

try:
    from langchain_core.messages import HumanMessage
    from langgraph.graph import END, StateGraph
    from typing import TypedDict, Annotated
    from operator import add
except ImportError:
    print("This example requires langgraph and langchain-core.")
    print("Install with: pip install langgraph langchain-core")
    sys.exit(1)


# --- Define a simple agent graph ---


class AgentState(TypedDict):
    messages: Annotated[list, add]
    step_count: int


def planner(state: AgentState) -> dict:
    """Planning node — decides what to do next."""
    return {
        "messages": [{"role": "assistant", "content": "I'll search for that information."}],
        "step_count": state.get("step_count", 0) + 1,
    }


def search_tool(state: AgentState) -> dict:
    """Tool node — simulates a search."""
    query = state["messages"][-1] if state["messages"] else "default query"
    return {
        "messages": [{"role": "tool", "content": f"Search results for: {query}"}],
        "step_count": state.get("step_count", 0) + 1,
    }


def responder(state: AgentState) -> dict:
    """LLM node — generates the final response."""
    return {
        "messages": [{"role": "assistant", "content": "Based on my research, here is your answer."}],
        "step_count": state.get("step_count", 0) + 1,
    }


def build_graph():
    """Build a simple linear agent graph: planner → search → responder."""
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner)
    graph.add_node("search_tool", search_tool)
    graph.add_node("responder", responder)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "search_tool")
    graph.add_edge("search_tool", "responder")
    graph.add_edge("responder", END)

    return graph.compile()


def main():
    """Run the example agent with StateLens instrumentation."""
    print("🔍 StateLens Example — Simple Agent")
    print("=" * 40)

    # Build the graph
    app = build_graph()

    # ✨ One line to instrument — that's it!
    app = observe(app)

    # Run the agent
    print("\n▶ Running agent...")
    result = app.invoke({
        "messages": [{"role": "user", "content": "What is StateLens?"}],
        "step_count": 0,
    })

    print(f"\n✅ Agent completed in {result['step_count']} steps")
    print(f"   Messages: {len(result['messages'])}")

    # Show where the data is stored
    from statelens.storage import get_db_path
    print(f"\n📁 Events stored in: {get_db_path()}")
    print("   Run 'statelens-server' and open http://localhost:8000/conversations")


if __name__ == "__main__":
    main()
