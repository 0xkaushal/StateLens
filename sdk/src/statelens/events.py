"""StateLens SDK — Canonical Event Model.

Mirrors contracts/event.schema.json exactly.
This is the single Python representation of the Event schema.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class NodeType(StrEnum):
    """Category of a graph node."""

    LLM = "llm"
    TOOL = "tool"
    MEMORY = "memory"
    PLANNER = "planner"
    ROUTER = "router"


class EventStatus(StrEnum):
    """Outcome of a node execution."""

    SUCCESS = "success"
    FAILED = "failed"


class Event(BaseModel):
    """Canonical event — one per node execution step.

    Every field matches contracts/event.schema.json.
    """

    conversation_id: str = Field(
        ...,
        alias="conversationId",
        description="Groups events into a single execution run.",
    )
    node_id: str = Field(
        ...,
        alias="nodeId",
        description="Unique ID for this node execution instance.",
    )
    node_name: str = Field(
        ...,
        alias="nodeName",
        description="Human-readable node name.",
    )
    node_type: NodeType = Field(
        ...,
        alias="nodeType",
        description="Category of the node.",
    )
    start_time: datetime = Field(
        ...,
        alias="startTime",
        description="When execution started (UTC).",
    )
    end_time: datetime = Field(
        ...,
        alias="endTime",
        description="When execution ended (UTC).",
    )
    latency_ms: float = Field(
        ...,
        alias="latencyMs",
        ge=0,
        description="Duration in milliseconds.",
    )
    status: EventStatus = Field(
        ...,
        description="success or failed.",
    )
    input: dict = Field(
        default_factory=dict,
        description="Input passed to the node.",
    )
    output: dict = Field(
        default_factory=dict,
        description="Output produced by the node.",
    )
    state_before: dict = Field(
        default_factory=dict,
        alias="stateBefore",
        description="Graph state before this node executed.",
    )
    state_after: dict = Field(
        default_factory=dict,
        alias="stateAfter",
        description="Graph state after this node executed.",
    )
    error: str | None = Field(
        default=None,
        description="Error message if status is 'failed'.",
    )

    model_config = {
        "populate_by_name": True,
        "json_schema_extra": {
            "examples": [
                {
                    "conversationId": "550e8400-e29b-41d4-a716-446655440000",
                    "nodeId": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                    "nodeName": "agent",
                    "nodeType": "llm",
                    "startTime": "2025-07-25T10:00:00Z",
                    "endTime": "2025-07-25T10:00:02Z",
                    "latencyMs": 2000,
                    "status": "success",
                    "input": {"messages": [{"role": "user", "content": "hello"}]},
                    "output": {"messages": [{"role": "assistant", "content": "hi"}]},
                    "stateBefore": {"messages": []},
                    "stateAfter": {"messages": [{"role": "user", "content": "hello"}]},
                    "error": None,
                }
            ]
        },
    }
