"""Tests for statelens.storage — SQLite storage implementation."""

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import pytest

from statelens.events import Event, EventStatus, NodeType
from statelens.storage import SQLiteStorage, get_db_path


def _make_event(**overrides) -> Event:
    """Factory for creating test events."""
    defaults = {
        "conversation_id": "conv-test-001",
        "node_id": "node-test-001",
        "node_name": "test_node",
        "node_type": NodeType.LLM,
        "start_time": datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
        "end_time": datetime(2025, 7, 25, 10, 0, 2, tzinfo=UTC),
        "latency_ms": 2000.0,
        "status": EventStatus.SUCCESS,
        "input": {"query": "test"},
        "output": {"result": "ok"},
        "state_before": {"step": 0},
        "state_after": {"step": 1},
    }
    defaults.update(overrides)
    return Event(**defaults)


class TestGetDbPath:
    def test_default_path(self, monkeypatch):
        monkeypatch.delenv("STATELENS_DB_PATH", raising=False)
        path = get_db_path()
        assert path == Path.home() / ".statelens" / "statelens.db"

    def test_custom_path_from_env(self, monkeypatch):
        monkeypatch.setenv("STATELENS_DB_PATH", "/tmp/custom.db")
        path = get_db_path()
        assert path == Path("/tmp/custom.db")


class TestSQLiteStorage:
    @pytest.fixture
    def storage(self, tmp_path):
        """Create a storage instance with a temp database."""
        db_path = tmp_path / "test.db"
        s = SQLiteStorage(db_path=db_path)
        yield s
        s.close()

    def test_creates_database_file(self, tmp_path):
        db_path = tmp_path / "new.db"
        assert not db_path.exists()
        s = SQLiteStorage(db_path=db_path)
        assert db_path.exists()
        s.close()

    def test_creates_events_table(self, storage):
        # Query sqlite_master to verify table exists
        cursor = storage._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='events'"
        )
        assert cursor.fetchone() is not None

    def test_save_event(self, storage):
        event = _make_event()
        storage.save_event(event)

        cursor = storage._conn.execute(
            "SELECT * FROM events WHERE node_id = ?", (event.node_id,)
        )
        row = cursor.fetchone()
        assert row is not None

    def test_save_event_persists_all_fields(self, storage):
        event = _make_event(
            node_name="my_tool",
            node_type=NodeType.TOOL,
            status=EventStatus.FAILED,
            error="timeout",
        )
        storage.save_event(event)

        cursor = storage._conn.execute(
            "SELECT * FROM events WHERE node_id = ?", (event.node_id,)
        )
        row = cursor.fetchone()

        assert row[0] == event.node_id  # node_id (PK)
        assert row[1] == event.conversation_id
        assert row[2] == "my_tool"
        assert row[3] == "tool"
        assert row[7] == "failed"
        assert row[12] == "timeout"

    def test_save_event_serializes_json_fields(self, storage):
        input_data = {"messages": [{"role": "user", "content": "hello"}]}
        event = _make_event(input=input_data)
        storage.save_event(event)

        cursor = storage._conn.execute(
            "SELECT input FROM events WHERE node_id = ?", (event.node_id,)
        )
        row = cursor.fetchone()
        assert json.loads(row[0]) == input_data

    def test_save_event_upsert(self, storage):
        """INSERT OR REPLACE should update existing events."""
        event = _make_event(node_id="same-id", node_name="original")
        storage.save_event(event)

        updated = _make_event(node_id="same-id", node_name="updated")
        storage.save_event(updated)

        cursor = storage._conn.execute(
            "SELECT node_name FROM events WHERE node_id = 'same-id'"
        )
        row = cursor.fetchone()
        assert row[0] == "updated"

    def test_multiple_events_same_conversation(self, storage):
        for i in range(5):
            event = _make_event(node_id=f"node-{i}", conversation_id="same-conv")
            storage.save_event(event)

        cursor = storage._conn.execute(
            "SELECT COUNT(*) FROM events WHERE conversation_id = 'same-conv'"
        )
        assert cursor.fetchone()[0] == 5

    def test_close_and_reopen(self, tmp_path):
        db_path = tmp_path / "reopen.db"
        s1 = SQLiteStorage(db_path=db_path)
        s1.save_event(_make_event(node_id="persistent"))
        s1.close()

        s2 = SQLiteStorage(db_path=db_path)
        cursor = s2._conn.execute(
            "SELECT node_id FROM events WHERE node_id = 'persistent'"
        )
        assert cursor.fetchone() is not None
        s2.close()
