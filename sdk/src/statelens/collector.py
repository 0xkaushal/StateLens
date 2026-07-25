"""StateLens SDK — Event Collector.

Receives raw callback data from the LangGraph handler,
builds canonical Event objects, and passes them to storage.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from statelens.events import Event, EventStatus, NodeType
from statelens.storage import SQLiteStorage, Storage


class Collector:
    """Collects execution events and persists them via the storage layer."""

    def __init__(self, conversation_id: str | None = None, storage: Storage | None = None) -> None:
        self._conversation_id = conversation_id or str(uuid.uuid4())
        self._storage = storage or SQLiteStorage()

    @property
    def conversation_id(self) -> str:
        return self._conversation_id

    def record_event(
        self,
        *,
        node_name: str,
        node_type: NodeType,
        start_time: datetime,
        end_time: datetime,
        input_data: dict,
        output_data: dict,
        state_before: dict,
        state_after: dict,
        status: EventStatus = EventStatus.SUCCESS,
        error: str | None = None,
    ) -> Event:
        """Build and persist a single Event.

        Returns the created Event for inspection/testing.
        """
        latency_ms = (end_time - start_time).total_seconds() * 1000

        event = Event(
            conversation_id=self._conversation_id,
            node_id=str(uuid.uuid4()),
            node_name=node_name,
            node_type=node_type,
            start_time=start_time,
            end_time=end_time,
            latency_ms=latency_ms,
            status=status,
            input=input_data,
            output=output_data,
            state_before=state_before,
            state_after=state_after,
            error=error,
        )

        self._storage.save_event(event)
        return event

    def close(self) -> None:
        """Release storage resources."""
        self._storage.close()
