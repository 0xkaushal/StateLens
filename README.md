# StateLens

> **Chrome DevTools for AI Agents**

StateLens is a local-first debugging workspace for AI applications. Inspect every node, state transition, tool call, prompt, and execution path in your LangGraph agents.

---

## Quick Start

### 1. Install the SDK

```bash
cd sdk
uv sync --extra langgraph
# or: pip install -e ".[langgraph]"
```

### 2. Instrument your graph

```python
from statelens import observe

app = graph.compile()
app = observe(app)  # ← one line, zero config

result = app.invoke({"messages": [...]})
```

### 3. Start the server

```bash
cd backend
uv sync
statelens-server
```

### 4. View your executions

Open [http://localhost:8000/conversations](http://localhost:8000/conversations)

---

## Architecture

```
SDK (writes)  →  SQLite (~/.statelens/statelens.db)  ←  Backend (reads)  →  Frontend (displays)
```

- **SDK** — instruments LangGraph via callbacks, writes events to SQLite
- **Backend** — FastAPI server, reads from the same SQLite, serves REST API
- **Frontend** — Next.js app (separate repo concern), consumes the REST API

---

## Project Structure

```
statelens/
├── contracts/      # Shared schemas and API contracts
├── sdk/            # Python SDK (statelens-sdk package)
├── backend/        # FastAPI server (statelens-server package)
├── frontend/       # Next.js UI (managed by OpenCode)
├── examples/       # Example LangGraph apps
└── docs/           # Documentation
```

---

## API Endpoints

| Method | Path                       | Description                  |
|--------|----------------------------|------------------------------|
| GET    | /health                    | Health check                 |
| GET    | /conversations             | List all conversations       |
| GET    | /conversations/{id}        | Get conversation with events |
| GET    | /events/{conversationId}   | Get events for a conversation|

---

## Configuration

| Env Variable        | Default                      | Description          |
|---------------------|------------------------------|----------------------|
| STATELENS_DB_PATH   | ~/.statelens/statelens.db    | SQLite database path |
| STATELENS_HOST      | 127.0.0.1                    | Server bind address  |
| STATELENS_PORT      | 8000                         | Server port          |

---

## License

MIT
