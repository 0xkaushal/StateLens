"""Tests for statelens.collector — Event collection."""

from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from statelens.collector import Collector
from statelens.events import EventStatus, NodeType
from statelens.storage import Storage


class TestCollector:
    @pytest.fixture
    def mock_storage(self):
        """Mock storage to avoid SQLite in unit tests."""
        storage = MagicMock(spec=Storage)
        return storage

    @pytest.fixture
    def collector(self, mock_storage):
        return Collector(conversation_id="test-conv-001", storage=mock_storage)

    def test_generates_conversation_id_if_not_provided(self):
        c = Collector(storage=MagicMock(spec=Storage))
        assert c.conversation_id is not None
        assert len(c.conversation_id) == 36  # UUID format

    def test_uses_provided_conversation_id(self, collector):
        assert collector.conversation_id == "test-conv-001"

    def test_record_event_calls_storage(self, collector, mock_storage):
        collector.record_event(
            node_name="test_node",
            node_type=NodeType.LLM,
            start_time=datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 2, tzinfo=UTC),
            input_data={"q": "hello"},
            output_data={"a": "world"},
            state_before={},
            state_after={},
        )
        mock_storage.save_event.assert_called_once()

    def test_record_event_returns_event(self, collector):
        event = collector.record_event(
            node_name="my_tool",
            node_type=NodeType.TOOL,
            start_time=datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 1, tzinfo=UTC),
            input_data={"x": 1},
            output_data={"y": 2},
            state_before={"step": 0},
            state_after={"step": 1},
        )
        assert event.node_name == "my_tool"
        assert event.node_type == NodeType.TOOL
        assert event.conversation_id == "test-conv-001"
        assert event.status == EventStatus.SUCCESS

    def test_record_event_calculates_latency(self, collector):
        event = collector.record_event(
            node_name="slow_node",
            node_type=NodeType.LLM,
            start_time=datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 3, tzinfo=UTC),
            input_data={},
            output_data={},
            state_before={},
            state_after={},
        )
        assert event.latency_ms == 3000.0

    def test_record_failed_event(self, collector):
        event = collector.record_event(
            node_name="broken",
            node_type=NodeType.TOOL,
            start_time=datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 1, tzinfo=UTC),
            input_data={},
            output_data={},
            state_before={},
            state_after={},
            status=EventStatus.FAILED,
            error="Connection timeout",
        )
        assert event.status == EventStatus.FAILED
        assert event.error == "Connection timeout"

    def test_each_event_gets_unique_node_id(self, collector):
        e1 = collector.record_event(
            node_name="a", node_type=NodeType.LLM,
            start_time=datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 1, tzinfo=UTC),
            input_data={}, output_data={}, state_before={}, state_after={},
        )
        e2 = collector.record_event(
            node_name="b", node_type=NodeType.LLM,
            start_time=datetime(2025, 7, 25, 10, 0, 1, tzinfo=UTC),
            end_time=datetime(2025, 7, 25, 10, 0, 2, tzinfo=UTC),
            input_data={}, output_data={}, state_before={}, state_after={},
        )
        assert e1.node_id != e2.node_id

    def test_close_delegates_to_storage(self, collector, mock_storage):
        collector.close()
        mock_storage.close.assert_called_once()
