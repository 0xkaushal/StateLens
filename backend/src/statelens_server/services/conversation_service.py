"""StateLens Server — Conversation Service.

Business logic for querying conversations. No SQL here — delegates to database layer.
"""

from __future__ import annotations

import json

from statelens_server.database.connection import db
from statelens_server.database.queries import (
    GET_CONVERSATION,
    GET_EVENTS_BY_CONVERSATION,
    LIST_CONVERSATIONS,
)
from statelens_server.schemas.responses import (
    ConversationDetail,
    ConversationSummary,
    EventResponse,
)


def list_conversations() -> list[ConversationSummary]:
    """Get all conversations, most recent first."""
    with db.cursor() as cursor:
        if cursor is None:
            return []

        cursor.execute(LIST_CONVERSATIONS)
        rows = cursor.fetchall()

    return [
        ConversationSummary(
            id=row["id"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            node_count=row["node_count"],
            status=row["status"],
        )
        for row in rows
    ]


def get_conversation(conversation_id: str) -> ConversationDetail | None:
    """Get a single conversation with all its events."""
    with db.cursor() as cursor:
        if cursor is None:
            return None

        # Get conversation summary
        cursor.execute(GET_CONVERSATION, (conversation_id,))
        conv_row = cursor.fetchone()
        if conv_row is None:
            return None

        # Get events
        cursor.execute(GET_EVENTS_BY_CONVERSATION, (conversation_id,))
        event_rows = cursor.fetchall()

    events = [_row_to_event(row) for row in event_rows]

    return ConversationDetail(
        id=conv_row["id"],
        start_time=conv_row["start_time"],
        end_time=conv_row["end_time"],
        node_count=conv_row["node_count"],
        status=conv_row["status"],
        events=events,
    )


def _row_to_event(row: dict) -> EventResponse:
    """Convert a database row to an EventResponse."""
    return EventResponse(
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
