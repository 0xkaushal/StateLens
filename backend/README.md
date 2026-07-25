# statelens-server

> FastAPI backend for StateLens — serves execution data to the frontend.

## Install

```bash
pip install statelens-server
# or with uv:
uv add statelens-server
```

## Run

```bash
# As a CLI command:
statelens-server

# Or with uvicorn directly:
uvicorn statelens_server.main:app --host 127.0.0.1 --port 8000

# With hot reload (development):
uvicorn statelens_server.main:app --reload
```

Server starts at http://localhost:8000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check → `{"status": "ok", "version": "0.1.0"}` |
| GET | `/conversations` | List all conversations (most recent first) |
| GET | `/conversations/{id}` | Get one conversation with all its events |
| GET | `/events/{conversationId}` | Get events for a conversation |

## Architecture

```
SDK writes → SQLite (~/.statelens/statelens.db) ← Backend reads → REST API → Frontend
```

The backend is **read-only**. It never writes to the database. The SDK handles all writes.

### Layer structure

```
routes/       → Thin HTTP handlers (no logic)
services/     → Business logic (query + transform)
database/     → SQLite connection + raw SQL queries
schemas/      → Pydantic response models
config/       → Settings + feature flags
```

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `STATELENS_DB_PATH` | `~/.statelens/statelens.db` | Path to the SQLite database |
| `STATELENS_HOST` | `127.0.0.1` | Bind address |
| `STATELENS_PORT` | `8000` | Port |
| `STATELENS_CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS allowed origins |

## Feature Flags

All features are gated via env vars. Current flags:

| Flag | Default | Description |
|------|---------|-------------|
| `FEATURE_LANGGRAPH` | true | LangGraph support enabled |
| `FEATURE_SQLITE_STORAGE` | true | SQLite storage enabled |
| `FEATURE_PROMPT_DIFF` | false | Prompt diff comparison (roadmap) |
| `FEATURE_STATE_DIFF` | false | State diff comparison (roadmap) |
| `FEATURE_ROOT_CAUSE_ANALYSIS` | false | AI-powered root cause analysis (roadmap) |
| `FEATURE_EXPORT_TRACE` | false | Export execution traces (roadmap) |

## Development

```bash
cd backend
uv sync --extra dev
pytest
```

## What happens if the database doesn't exist?

The server starts normally and returns empty results. Once the SDK writes its first event, the server will pick it up on the next request (it reconnects lazily).
