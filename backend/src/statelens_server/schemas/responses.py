"""StateLens Server — Pydantic Response Schemas.

Shapes that the API returns to the frontend.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


class ConversationSummary(BaseModel):
    """Compact conversation representation for the list view."""

    id: str
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    node_count: int = Field(..., alias="nodeCount")
    status: str

    model_config = {"populate_by_name": True}


class EventResponse(BaseModel):
    """Full event for the detail view."""

    conversation_id: str = Field(..., alias="conversationId")
    node_id: str = Field(..., alias="nodeId")
    node_name: str = Field(..., alias="nodeName")
    node_type: str = Field(..., alias="nodeType")
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    latency_ms: float = Field(..., alias="latencyMs")
    status: str
    input: dict
    output: dict
    state_before: dict = Field(..., alias="stateBefore")
    state_after: dict = Field(..., alias="stateAfter")
    error: str | None = None

    model_config = {"populate_by_name": True}


class ConversationDetail(BaseModel):
    """Full conversation with events for the detail view."""

    id: str
    start_time: str = Field(..., alias="startTime")
    end_time: str = Field(..., alias="endTime")
    node_count: int = Field(..., alias="nodeCount")
    status: str
    events: list[EventResponse]

    model_config = {"populate_by_name": True}
