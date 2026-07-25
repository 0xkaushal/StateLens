# StateLens — Shared Type Definitions

All modules (SDK, Backend, Frontend) must use these types exactly as defined.

No module may invent new fields without updating this file first.

---

## Enums

### NodeType

```
llm       — Language model invocation
tool      — Tool/function call
memory    — Memory read/write
planner   — Planning/reasoning step
router    — Routing/conditional decision
```

### EventStatus

```
success   — Node completed without error
failed    — Node threw an exception or returned error
```

---

## Core Models

### Event

The atomic unit of StateLens. Every node execution produces exactly one Event.

| Field            | Type       | Required | Description                              |
|------------------|------------|----------|------------------------------------------|
| conversationId   | string     | ✅       | Groups events into a single execution run |
| nodeId           | string     | ✅       | Unique ID for this node execution         |
| nodeName         | string     | ✅       | Human-readable node name                  |
| nodeType         | NodeType   | ✅       | Category of the node                      |
| startTime        | ISO 8601   | ✅       | When execution started                    |
| endTime          | ISO 8601   | ✅       | When execution ended                      |
| latencyMs        | number     | ✅       | Duration in milliseconds                  |
| status           | EventStatus| ✅       | success or failed                         |
| input            | object     | ✅       | Input to the node                         |
| output           | object     | ✅       | Output from the node                      |
| stateBefore      | object     | ✅       | Graph state before execution              |
| stateAfter       | object     | ✅       | Graph state after execution               |
| error            | string     | ❌       | Error message (only when status=failed)   |

### Conversation

A logical grouping of Events that belong to one agent execution.

| Field            | Type       | Required | Description                              |
|------------------|------------|----------|------------------------------------------|
| id               | string     | ✅       | Same as conversationId in events          |
| title            | string     | ✅       | Derived from first user message (max 60 chars) |
| createdAt        | ISO 8601   | ✅       | Earliest event startTime                  |
| updatedAt        | ISO 8601   | ✅       | Latest event endTime                      |
| totalEvents      | number     | ✅       | Total number of events                    |
| totalLatencyMs   | number     | ✅       | Sum of all event latencies in ms          |
| status           | EventStatus| ✅       | failed if any event failed, else success  |

---

## Conventions

- All timestamps are UTC ISO 8601 strings
- All IDs are UUIDs (v4)
- All JSON objects use camelCase keys
- `input` and `output` are arbitrary JSON — their shape depends on the node
- `stateBefore` and `stateAfter` are the full LangGraph state dict serialized as JSON
