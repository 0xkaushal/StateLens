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


def _derive_title(first_input_json: str | None, conversation_id: str) -> str:
    """Derive a conversation title from the first event's input.

    Attempts to extract the first user message. Falls back to a short ID.
    """
    if first_input_json:
        try:
            data = json.loads(first_input_json)
            # Try to find a user message in the input
            messages = data.get("messages", [])
            if isinstance(messages, list):
                for msg in messages:
                    if isinstance(msg, dict) and msg.get("role") == "user":
                        content = msg.get("content", "")
                        if content:
                            # Truncate to 60 chars for readability
                            return content[:60] + ("..." if len(content) > 60 else "")
        except (json.JSONDecodeError, TypeError):
            pass

    # Fallback: short conversation ID
    return f"Conversation {conversation_id[:8]}"


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
            title=_derive_title(row["first_input"], row["id"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            total_events=row["total_events"],
            total_latency_ms=row["total_latency_ms"],
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
        title=_derive_title(conv_row["first_input"], conv_row["id"]),
        created_at=conv_row["created_at"],
        updated_at=conv_row["updated_at"],
        total_events=conv_row["total_events"],
        total_latency_ms=conv_row["total_latency_ms"],
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
