# StateLens — REST API Contract

Base URL: `http://localhost:8000`

All responses are JSON. All endpoints are GET (read-only server).

---

## Endpoints

### GET /health

Health check.

**Response 200**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

### GET /conversations

List all recorded conversations, most recent first.

**Response 200**
```json
[
  {
    "id": "uuid-string",
    "startTime": "2025-07-25T10:00:00Z",
    "endTime": "2025-07-25T10:00:05Z",
    "nodeCount": 4,
    "status": "success"
  }
]
```

---

### GET /conversations/{id}

Get a single conversation with its events.

**Path Parameters**
- `id` — conversation UUID

**Response 200**
```json
{
  "id": "uuid-string",
  "startTime": "2025-07-25T10:00:00Z",
  "endTime": "2025-07-25T10:00:05Z",
  "nodeCount": 4,
  "status": "success",
  "events": [
    { "...Event object..." }
  ]
}
```

**Response 404**
```json
{
  "detail": "Conversation not found"
}
```

---

### GET /events/{conversationId}

Get all events for a conversation, ordered by startTime.

**Path Parameters**
- `conversationId` — conversation UUID

**Response 200**
```json
[
  {
    "conversationId": "uuid-string",
    "nodeId": "uuid-string",
    "nodeName": "agent",
    "nodeType": "llm",
    "startTime": "2025-07-25T10:00:00Z",
    "endTime": "2025-07-25T10:00:02Z",
    "latencyMs": 2000,
    "status": "success",
    "input": {},
    "output": {},
    "stateBefore": {},
    "stateAfter": {},
    "error": null
  }
]
```

**Response 200 (empty)**
```json
[]
```

Returns an empty array if no events exist for the given conversationId.

---

## Error Format

All errors follow this shape:

```json
{
  "detail": "Human-readable error message"
}
```

---

## CORS

The server enables CORS for `http://localhost:3000` (Next.js dev server) by default.

---

## Versioning

No API versioning in MVP. The contract is simple and stable.
Future versions will use `/v2/` prefix if breaking changes are needed.
