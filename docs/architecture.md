# StateLens Architecture

## Overview

StateLens is a local-first debugging tool for AI agents. It has three independent modules that communicate through shared contracts.

```
┌─────────────────────────────────────────────────────────────┐
│                         User's App                           │
│                                                             │
│   from statelens import observe                             │
│   app = observe(graph.compile())                            │
│   app.invoke(...)                                           │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ LangGraph callbacks
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                        SDK (writes)                          │
│                                                             │
│   observe.py → langgraph.py → collector.py → storage.py     │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ SQLite INSERT
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│              ~/.statelens/statelens.db                       │
│                                                             │
│   ┌──────────────────────────────────────────────────┐     │
│   │ events table                                      │     │
│   │   node_id | conversation_id | node_name | ...     │     │
│   └──────────────────────────────────────────────────┘     │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ SQLite SELECT (read-only)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Backend (reads)                          │
│                                                             │
│   main.py → routes/ → services/ → database/                 │
│                                                             │
│   GET /health                                               │
│   GET /conversations                                        │
│   GET /conversations/{id}                                   │
│   GET /events/{conversationId}                              │
│                                                             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             │ REST API (JSON)
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (displays)                      │
│                                                             │
│   Next.js + React + Tailwind + React Flow                   │
│                                                             │
│   Conversation List → Timeline → Execution Graph            │
│   Node Inspector → Prompt Viewer → State Viewer             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Write Path (SDK → SQLite)

1. User calls `app.invoke(input)`
2. `observe()` injects our `StateLensCallbackHandler` into the config
3. LangGraph fires callbacks: `on_chain_start`, `on_chain_end`, `on_tool_start`, etc.
4. Handler builds Event objects via `Collector`
5. `SQLiteStorage.save_event()` writes to `~/.statelens/statelens.db`

### Read Path (SQLite → Backend → Frontend)

1. Frontend calls `GET /conversations`
2. Backend route delegates to `conversation_service.list_conversations()`
3. Service executes SQL from `database/queries.py`
4. Results are mapped to Pydantic `ConversationSummary` models
5. FastAPI serializes to JSON with camelCase keys
6. Frontend renders the data

---

## Key Design Decisions

### 1. Shared SQLite (not HTTP between SDK and Backend)

**Why:** Local-first means same machine. SQLite WAL mode supports concurrent readers + one writer. No network overhead, no server required during execution.

**Trade-off:** SDK and backend must agree on the DB path. Solved via `STATELENS_DB_PATH` env var with a sensible default (`~/.statelens/statelens.db`).

### 2. Callbacks (not monkey-patching)

**Why:** LangGraph/LangChain have a stable callback system. Using it means we don't break on LangGraph version upgrades.

**Trade-off:** We only capture what callbacks expose. If LangGraph adds new event types, we need to add new handler methods.

### 3. Storage Interface Pattern

**Why:** Decouples from SQLite. Tomorrow we could add Postgres, cloud storage, or an in-memory implementation for testing — without changing any other code.

### 4. Feature Flags Everywhere

**Why:** Every feature can be independently enabled/disabled/tested/removed. Allows safe incremental development and easy rollback.

### 5. Two Separate Packages

**Why:** Users who only want instrumentation (`statelens-sdk`) shouldn't carry FastAPI as a dependency. The server is a separate tool they run when they want to debug.

---

## Module Boundaries

| Rule | Meaning |
|------|---------|
| SDK → SQLite | SDK writes events directly. Never calls the backend. |
| Backend → SQLite | Backend reads only. Never writes. |
| Frontend → Backend | Frontend calls REST API. Never touches SQLite. |
| SDK ≠ Backend | SDK doesn't import anything from backend. |
| Backend ≠ Frontend | Backend knows nothing about React/Next.js. |

---

## SQLite Schema

```sql
CREATE TABLE events (
    node_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    node_type TEXT NOT NULL,        -- llm | tool | memory | planner | router
    start_time TEXT NOT NULL,       -- ISO 8601
    end_time TEXT NOT NULL,         -- ISO 8601
    latency_ms REAL NOT NULL,
    status TEXT NOT NULL,           -- success | failed
    input TEXT NOT NULL DEFAULT '{}',       -- JSON
    output TEXT NOT NULL DEFAULT '{}',      -- JSON
    state_before TEXT NOT NULL DEFAULT '{}', -- JSON
    state_after TEXT NOT NULL DEFAULT '{}',  -- JSON
    error TEXT                      -- NULL if success
);

CREATE INDEX idx_events_conversation_id ON events (conversation_id);
CREATE INDEX idx_events_start_time ON events (start_time);
```

- PRAGMAs: `journal_mode=WAL`, `busy_timeout=5000`
- Backend adds: `query_only=ON`

---

## Concurrency Model

- **SDK:** Single-writer. One `SQLiteStorage` instance per `observe()` call. WAL mode allows the backend to read concurrently.
- **Backend:** Multi-reader. FastAPI handles concurrent HTTP requests. Each reads from the same SQLite connection (read-only, no contention).
- **Frontend:** Standard SPA. Polls or refetches when user navigates.
