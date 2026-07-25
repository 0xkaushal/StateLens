"""StateLens Server — SQLite Connection Manager.

Provides a read-only connection to the shared SQLite database.
The SDK writes; the backend only reads.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

from statelens_server.config.settings import DB_PATH


class Database:
    """Manages the SQLite connection for read-only queries."""

    def __init__(self, db_path: Path | None = None) -> None:
        self._db_path = db_path or DB_PATH
        self._conn: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Open the database connection."""
        if not self._db_path.exists():
            # Database hasn't been created by the SDK yet — that's okay.
            # We'll return empty results until it exists.
            return

        self._conn = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA query_only=ON")

    def close(self) -> None:
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor | None, None, None]:
        """Get a cursor, or None if DB doesn't exist yet."""
        if self._conn is None:
            # Try to connect — DB may have been created since startup
            self.connect()

        if self._conn is None:
            yield None
        else:
            cursor = self._conn.cursor()
            try:
                yield cursor
            finally:
                cursor.close()


# Singleton instance — created at startup, shared across requests.
db = Database()
