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
    start_time: datetime = Field(
        ...,
        alias="startTime",
        description="Earliest event start time.",
    )
    end_time: datetime = Field(
        ...,
        alias="endTime",
        description="Latest event end time.",
    )
    node_count: int = Field(
        ...,
        alias="nodeCount",
        ge=0,
        description="Total number of events.",
    )
    status: EventStatus = Field(
        ...,
        description="failed if any event failed, else success.",
    )

    model_config = {"populate_by_name": True}
