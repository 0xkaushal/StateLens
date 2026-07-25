"""StateLens SDK — Event Collector.

Receives raw callback data from the LangGraph handler,
builds canonical Event objects, and passes them to storage.

Supports both sync and async storage backends transparently.
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime
from typing import Any

from statelens.events import Event, EventStatus, NodeType
from statelens.storage import AsyncStorage, SQLiteStorage, Storage


class Collector:
    """Collects execution events and persists them via the storage layer.

    Works with both sync (Storage) and async (AsyncStorage) backends.
    When given an AsyncStorage, writes are fire-and-forget from sync callbacks
    (scheduled on the running event loop if one exists).
    """

    def __init__(self, conversation_id: str | None = None, storage: Storage | AsyncStorage | None = None) -> None:
        self._conversation_id = conversation_id or str(uuid.uuid4())
        self._storage = storage or SQLiteStorage()
        self._is_async = isinstance(self._storage, AsyncStorage)

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

        If using async storage, the write is scheduled as a fire-and-forget
        task on the running event loop. This means the LangGraph callback
        returns immediately without waiting for the disk write.

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

        if self._is_async:
            # Schedule the async write without blocking the callback
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._storage.save_event(event))
            except RuntimeError:
                # No running event loop — fall back to sync-in-thread
                # This can happen if observe() is used with async_storage=True
                # but the callback fires from a sync context.
                asyncio.run(self._storage.save_event(event))
        else:
            self._storage.save_event(event)

        return event

    def close(self) -> None:
        """Release storage resources."""
        if self._is_async:
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self._storage.close())
            except RuntimeError:
                asyncio.run(self._storage.close())
        else:
            self._storage.close()
