"""StateLens Server — Event Service.

Business logic for querying events.
"""

from __future__ import annotations

import json

from statelens_server.database.connection import db
from statelens_server.database.queries import GET_EVENTS_BY_CONVERSATION
from statelens_server.schemas.responses import EventResponse


def get_events(conversation_id: str) -> list[EventResponse]:
    """Get all events for a conversation, ordered by start time."""
    with db.cursor() as cursor:
        if cursor is None:
            return []

        cursor.execute(GET_EVENTS_BY_CONVERSATION, (conversation_id,))
        rows = cursor.fetchall()

    return [
        EventResponse(
            conversation_id=row["conversation_id"],
            node_id=row["node_id"],
            node_name=row["node_name"],
            node_type=row["node_type"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            latency_ms=row["latency_ms"],
            status=row["status"],
            input=json.loads(row["input"]),
            output=json.loads(row["output"]),
            state_before=json.loads(row["state_before"]),
            state_after=json.loads(row["state_after"]),
            error=row["error"],
        )
        for row in rows
    ]
