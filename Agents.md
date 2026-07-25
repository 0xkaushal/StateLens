# AGENTS.md

# StateLens

> **StateLens** — Chrome DevTools for AI Agents

StateLens is a local-first debugging workspace for AI applications. It enables developers to inspect, understand, and debug LangGraph execution by visualizing every node, state transition, tool call, prompt, and execution path.

The goal of StateLens is **not observability**.

The goal is **debugging**.

---

# Vision

Modern AI applications are difficult to debug.

A single request flows through multiple components:

- Planner
- Memory
- RAG
- LLM
- Tool Calls
- State Updates
- Routers
- Human Approval
- Additional Agents

When something goes wrong, engineers have to inspect logs spread across multiple systems.

StateLens should answer one question better than any other tool:

> **Why did my AI Agent do this?**

---

# Guiding Principles

## 1. Developer First

Every feature must reduce debugging time.

If a feature doesn't help an engineer debug an execution, it doesn't belong.

---

## 2. Local First

The MVP should run entirely on localhost.

No cloud.

No authentication.

No external services.

Technology

- SQLite
- FastAPI
- Next.js

---

## 3. Zero Configuration

Installation should be as close as possible to:

```python
from statelens import observe

graph = observe(graph)
```

No manual logging.

No decorators everywhere.

No complicated configuration.

---

## 4. Beautiful UX

StateLens should feel like

- Chrome DevTools
- VS Code Debugger
- Raycast
- Linear

NOT

- Grafana
- Kibana
- Datadog

---

## 5. Debuggable by Design

Every execution should expose

- Execution graph
- Timeline
- State transitions
- Prompt
- Tool calls
- Errors
- Latency

---

# Human + AI Development Workflow

This project is intentionally designed for **parallel AI-assisted development**.

The Human acts as the **Tech Lead**.

Claude Code and OpenCode act as implementation engineers.

The Human owns architecture.

AI owns implementation.

---

# Team Responsibilities

## Human (Tech Lead)

Owns

- Product decisions
- Architecture
- Contracts
- Feature prioritisation
- Code reviews
- Integration
- Merge conflicts
- Testing
- Release

---

## Claude Code

Primary Ownership

```
sdk/
backend/
contracts/
```

Responsibilities

- LangGraph instrumentation
- Event generation
- SQLite
- FastAPI
- Database models
- REST APIs
- Storage layer
- Serialization
- Error handling
- Unit Tests

Claude should NOT build UI.

---

## OpenCode

Primary Ownership

```
frontend/
```

Responsibilities

- Next.js
- React
- Tailwind
- React Flow
- Timeline
- Conversation List
- Execution Graph
- Node Inspector
- Prompt Viewer
- Tool Viewer
- State Viewer
- Landing Page

OpenCode should NEVER implement backend logic.

---

# Parallel Development Architecture

```
                  StateLens

             Shared Contracts
                    │
      ┌─────────────┼─────────────┐
      │             │             │
      ▼             ▼             ▼

     SDK         Backend      Frontend

      │             │             │

      └─────────────┼─────────────┘
                    │

              SQLite Database

                    │

          Example LangGraph App
```

Every module must be independently buildable.

---

# Repository Structure

```
statelens/

sdk/

backend/

frontend/

contracts/

examples/

docs/
```

---

# SDK Structure

```
sdk/

observe.py

collector.py

events.py

models.py

storage.py

langgraph.py

config.py
```

Responsibilities

observe.py

- Public API

collector.py

- Collect execution events

events.py

- Canonical Event model

storage.py

- Storage abstraction

langgraph.py

- LangGraph instrumentation

config.py

- Feature Flags

---

# Backend Structure

```
backend/

api/

routes/

services/

database/

models/

schemas/

config/
```

Responsibilities

- REST APIs
- Persistence
- Query layer
- Feature flags

No business logic inside routes.

---

# Frontend Structure

```
frontend/

app/

features/

shared/

hooks/

services/

types/

config/
```

Each feature lives independently.

Example

```
features/

conversation/

timeline/

execution-graph/

node-inspector/

prompt-viewer/

tool-viewer/

state-viewer/

execution-summary/

replay/

search/
```

Every feature owns

```
components/

hooks/

types/

api/

index.ts
```

---

# Contracts

Everything communicates through contracts.

Only these files define shared interfaces.

```
contracts/

event.schema.json

api.md

types.md
```

No module may invent new fields.

---

# Canonical Event Model

Every execution step creates exactly one Event.

```ts
interface Event {

    conversationId: string

    nodeId: string

    nodeName: string

    nodeType:
        | "llm"
        | "tool"
        | "memory"
        | "planner"
        | "router"

    startTime: string

    endTime: string

    latencyMs: number

    status:
        | "success"
        | "failed"

    input: object

    output: object

    stateBefore: object

    stateAfter: object

    error?: string
}
```

This schema is the foundation of the entire project.

---

# API Contract

Backend must expose

```
GET /health

GET /conversations

GET /conversation/{id}

GET /events/{conversationId}
```

These APIs must remain stable.

---

# Feature Flag Policy

Every feature MUST be behind a feature flag.

No feature may be hardcoded.

Every feature should be independently

- enabled
- disabled
- tested
- removed

without breaking the application.

---

# Environment Variables

Frontend

```env
NEXT_PUBLIC_FEATURE_TIMELINE=true
NEXT_PUBLIC_FEATURE_GRAPH_VIEW=true
NEXT_PUBLIC_FEATURE_NODE_INSPECTOR=true
NEXT_PUBLIC_FEATURE_PROMPT_VIEWER=true
NEXT_PUBLIC_FEATURE_TOOL_VIEWER=true
NEXT_PUBLIC_FEATURE_STATE_VIEWER=true
NEXT_PUBLIC_FEATURE_EXECUTION_SUMMARY=true
NEXT_PUBLIC_FEATURE_REPLAY=false
NEXT_PUBLIC_FEATURE_SEARCH=false
NEXT_PUBLIC_FEATURE_AI_SUMMARY=false
NEXT_PUBLIC_FEATURE_DARK_MODE=true
```

Backend

```env
FEATURE_LANGGRAPH=true
FEATURE_SQLITE_STORAGE=true

FEATURE_PROMPT_DIFF=false
FEATURE_STATE_DIFF=false
FEATURE_ROOT_CAUSE_ANALYSIS=false
FEATURE_FAILURE_CLUSTERING=false
FEATURE_EXPORT_TRACE=false
FEATURE_TRACE_COMPRESSION=false

FEATURE_OPENAI_AGENTS=false
FEATURE_MCP=false
FEATURE_CREWAI=false
FEATURE_MASTRA=false
```

---

# Feature Registry

Frontend

```
frontend/config/features.ts
```

Backend

```
backend/config/features.py
```

SDK

```
sdk/config.py
```

Every feature flag should be defined exactly once.

Never access environment variables directly outside these files.

---

# Feature Development Rules

Every new feature requires

✅ Environment Variable

✅ Registry Entry

✅ Documentation

✅ Graceful Fallback

A feature is NOT complete until all four exist.

---

# UI Rules

Never directly render optional features.

Instead

```tsx
{Features.nodeInspector && (
    <NodeInspector />
)}
```

---

# Backend Rules

Never execute optional functionality directly.

Instead

```python
if FEATURES["prompt_diff"]:
    run_prompt_diff(...)
```

---

# SDK Rules

Instrumentation should also be feature-gated.

```python
if FEATURES["langgraph"]:
    instrument_langgraph()

if FEATURES["mcp"]:
    instrument_mcp()
```

---

# Storage Layer

Never directly depend on SQLite.

Use

```
Storage Interface

↓

SQLite Storage

↓

Future

Postgres Storage

Cloud Storage
```

Changing storage should require changing exactly one implementation.

---

# Mock Data

Frontend development should NOT wait for Backend.

Frontend uses

```
frontend/mock/

conversation.json
```

Backend integration happens later.

---

# MVP Features

Must Build

✅ LangGraph Instrumentation

✅ Event Collection

✅ SQLite Storage

✅ FastAPI

✅ Conversation List

✅ Execution Graph

✅ Timeline

✅ Node Inspector

✅ Prompt Viewer

✅ Tool Viewer

✅ State Viewer

✅ Execution Summary

---

# Explicitly Out of Scope

Do NOT build

❌ Authentication

❌ User Accounts

❌ Teams

❌ RBAC

❌ Billing

❌ PostgreSQL

❌ Redis

❌ Kafka

❌ Kubernetes

❌ Cloud Sync

❌ OpenTelemetry

❌ LangSmith Integration

❌ Voice Playback

❌ Cost Analytics

❌ Notifications

❌ Slack

❌ Evaluation Pipelines

❌ Multi-project Support

---

# Code Quality

Prefer

- Composition
- Small modules
- Pure functions
- Typed interfaces
- Readable code

Avoid

- Deep inheritance
- Global mutable state
- Large files
- Premature optimisation

---

# Parallel Development Rules

Rule 1

Frontend should work entirely from mock data.

---

Rule 2

Backend should know nothing about UI.

---

Rule 3

SDK should know nothing about FastAPI.

---

Rule 4

Modules communicate ONLY through contracts.

---

Rule 5

No module imports another module's implementation.

Dependencies

```
Contracts

↓

SDK

↓

Backend

↓

Frontend
```

Never the reverse.

---

# Development Order

## Claude

1. Contracts

2. Event Model

3. SDK

4. SQLite

5. FastAPI

6. Example LangGraph App

---

## OpenCode

1. Landing Page

2. Conversation List

3. Timeline

4. Execution Graph

5. Node Inspector

6. Prompt Viewer

7. Tool Viewer

8. State Viewer

9. Execution Summary

---

## Human

1. Merge

2. Integration

3. Testing

4. Demo

---

# Definition of Done

A successful MVP allows a developer to

1. Install StateLens

2. Wrap a LangGraph application

3. Execute an Agent

4. Open localhost

5. View the execution graph

6. Inspect every node

7. View prompts

8. View tool calls

9. View state transitions

10. Understand failures without reading logs

If all ten steps work, the MVP is complete.

---

# Roadmap

## v0.2

- Replay Execution
- Prompt Diff
- State Diff
- Search
- Export Trace

## v0.3

- AI Root Cause Analysis
- Failure Clustering
- Prompt Version Comparison
- Replay From Node

## v0.4

- OpenAI Agents SDK
- MCP
- Mastra
- CrewAI
- AutoGen

## v1.0

Framework Agnostic AI Debugger

Cloud Sync

Enterprise Support

Multi-user Collaboration

Plugin Ecosystem

---

# North Star

StateLens should become the first application AI engineers open when an AI application behaves unexpectedly.

Just as software engineers instinctively reach for Chrome DevTools or a debugger, AI engineers should instinctively reach for **StateLens**.