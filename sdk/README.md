# statelens-sdk

> One-line instrumentation for LangGraph agents.

## Install

```bash
pip install statelens-sdk[langgraph]
# or with uv:
uv add statelens-sdk --extra langgraph
```

## Usage

```python
from statelens import observe
from langgraph.graph import StateGraph

# Build your graph as normal
graph = StateGraph(MyState)
graph.add_node("agent", agent_fn)
graph.add_node("tool", tool_fn)
# ...
app = graph.compile()

# ✨ One line — zero config
app = observe(app)

# Use it exactly as before
result = app.invoke({"messages": [{"role": "user", "content": "hello"}]})
```

That's it. Every node execution is now captured in `~/.statelens/statelens.db`.

## What gets captured

For every node execution:

| Field | Description |
|-------|-------------|
| conversationId | Groups all events from one `invoke()` call |
| nodeName | The node's name in your graph |
| nodeType | Inferred: llm, tool, memory, planner, router |
| startTime / endTime | When the node ran |
| latencyMs | How long it took |
| status | success or failed |
| input / output | What went in and came out |
| stateBefore / stateAfter | Full graph state snapshots |
| error | Error message if it failed |

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `STATELENS_DB_PATH` | `~/.statelens/statelens.db` | Where to store events |
| `FEATURE_LANGGRAPH` | `true` | Enable/disable instrumentation |

Set `FEATURE_LANGGRAPH=false` to disable without removing code.

## How it works

1. `observe(graph)` wraps the graph's `invoke`/`ainvoke`/`stream` methods
2. It injects a custom LangGraph callback handler
3. The handler listens for node start/end/error events
4. Each event is written to a local SQLite database
5. The StateLens backend server reads from the same database to serve the UI

## Development

```bash
cd sdk
uv sync --extra dev --extra langgraph
pytest
```
