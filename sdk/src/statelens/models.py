"""StateLens SDK — Data Models.

Supporting models beyond the core Event.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from statelens.events import EventStatus


class Conversation(BaseModel):
    """A logical grouping of Events from one agent execution."""

    id: str = Field(..., description="Conversation UUID.")
    title: str = Field(..., description="Derived title (first user message or short ID).")
    created_at: datetime = Field(
        ...,
        alias="createdAt",
        description="Earliest event start time.",
    )
    updated_at: datetime = Field(
        ...,
        alias="updatedAt",
        description="Latest event end time.",
    )
    total_events: int = Field(
        ...,
        alias="totalEvents",
        ge=0,
        description="Total number of events.",
    )
    total_latency_ms: float = Field(
        ...,
        alias="totalLatencyMs",
        ge=0,
        description="Sum of all event latencies in milliseconds.",
    )
    status: EventStatus = Field(
        ...,
        description="failed if any event failed, else success.",
    )

    model_config = {"populate_by_name": True}
