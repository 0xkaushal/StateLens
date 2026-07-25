# StateLens Examples

## simple_agent.py

A basic LangGraph agent that demonstrates StateLens instrumentation.

### Prerequisites

```bash
# From the repo root
cd sdk && pip install -e ".[langgraph]"
```

### Run

```bash
python examples/simple_agent.py
```

### View Results

```bash
cd backend && pip install -e .
statelens-server
# Open http://localhost:8000/conversations
```
