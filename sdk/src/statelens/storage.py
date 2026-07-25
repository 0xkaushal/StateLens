"""StateLens SDK — Storage Layer.

Provides a Storage protocol (ABC) and a SQLiteStorage implementation.
Never depend on SQLite directly outside this module.
"""

from __future__ import annotations

import json
import os
import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

from statelens.events import Event

# Default database path — shared between SDK and backend server.
DEFAULT_DB_PATH = Path.home() / ".statelens" / "statelens.db"


def get_db_path() -> Path:
    """Resolve database path from env or use default."""
    env_path = os.environ.get("STATELENS_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


class Storage(ABC):
    """Abstract storage interface.

    Changing storage backends should require changing exactly one implementation.
    """

    @abstractmethod
    def save_event(self, event: Event) -> None:
        """Persist a single event."""

    @abstractmethod
    def close(self) -> None:
        """Release resources."""


class SQLiteStorage(Storage):
    """SQLite-backed storage implementation.

    Creates the database and table if they don't exist.
    Thread-safe via SQLite's WAL mode.
    """

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or get_db_path()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=5000")
        self._create_tables()

    def _create_tables(self) -> None:
        """Create events table if it doesn't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                node_id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                node_name TEXT NOT NULL,
                node_type TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                latency_ms REAL NOT NULL,
                status TEXT NOT NULL,
                input TEXT NOT NULL DEFAULT '{}',
                output TEXT NOT NULL DEFAULT '{}',
                state_before TEXT NOT NULL DEFAULT '{}',
                state_after TEXT NOT NULL DEFAULT '{}',
                error TEXT
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_conversation_id
            ON events (conversation_id)
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_events_start_time
            ON events (start_time)
        """)
        self._conn.commit()

    def save_event(self, event: Event) -> None:
        """Insert an event into the database."""
        self._conn.execute(
            """
            INSERT OR REPLACE INTO events (
                node_id, conversation_id, node_name, node_type,
                start_time, end_time, latency_ms, status,
                input, output, state_before, state_after, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.node_id,
                event.conversation_id,
                event.node_name,
                event.node_type.value,
                event.start_time.isoformat(),
                event.end_time.isoformat(),
                event.latency_ms,
                event.status.value,
                json.dumps(event.input),
                json.dumps(event.output),
                json.dumps(event.state_before),
                json.dumps(event.state_after),
                event.error,
            ),
        )
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        self._conn.close()
