"""Tests for statelens.events — Event model validation."""

import pytest
from datetime import datetime, UTC

from statelens.events import Event, EventStatus, NodeType


class TestNodeType:
    def test_values(self):
        assert NodeType.LLM == "llm"
        assert NodeType.TOOL == "tool"
        assert NodeType.MEMORY == "memory"
        assert NodeType.PLANNER == "planner"
        assert NodeType.ROUTER == "router"

    def test_all_values_covered(self):
        assert len(NodeType) == 5


class TestEventStatus:
    def test_values(self):
        assert EventStatus.SUCCESS == "success"
        assert EventStatus.FAILED == "failed"


class TestEvent:
    def _make_event(self, **overrides) -> Event:
        """Factory for creating test events."""
        defaults = {
            "conversation_id": "conv-123",
            "node_id": "node-456",
            "node_name": "test_node",
            "node_type": NodeType.LLM,
            "start_time": datetime(2025, 7, 25, 10, 0, 0, tzinfo=UTC),
            "end_time": datetime(2025, 7, 25, 10, 0, 2, tzinfo=UTC),
            "latency_ms": 2000.0,
            "status": EventStatus.SUCCESS,
            "input": {"messages": [{"role": "user", "content": "hello"}]},
            "output": {"messages": [{"role": "assistant", "content": "hi"}]},
            "state_before": {"step": 0},
            "state_after": {"step": 1},
        }
        defaults.update(overrides)
        return Event(**defaults)

    def test_create_success_event(self):
        event = self._make_event()
        assert event.conversation_id == "conv-123"
        assert event.node_id == "node-456"
        assert event.node_name == "test_node"
        assert event.node_type == NodeType.LLM
        assert event.latency_ms == 2000.0
        assert event.status == EventStatus.SUCCESS
        assert event.error is None

    def test_create_failed_event(self):
        event = self._make_event(
            status=EventStatus.FAILED,
            error="Something broke",
        )
        assert event.status == EventStatus.FAILED
        assert event.error == "Something broke"

    def test_serialization_camel_case(self):
        event = self._make_event()
        data = event.model_dump(by_alias=True)
        assert "conversationId" in data
        assert "nodeId" in data
        assert "nodeName" in data
        assert "nodeType" in data
        assert "startTime" in data
        assert "endTime" in data
        assert "latencyMs" in data
        assert "stateBefore" in data
        assert "stateAfter" in data

    def test_deserialization_from_camel_case(self):
        data = {
            "conversationId": "conv-789",
            "nodeId": "node-abc",
            "nodeName": "agent",
            "nodeType": "tool",
            "startTime": "2025-07-25T10:00:00Z",
            "endTime": "2025-07-25T10:00:01Z",
            "latencyMs": 1000,
            "status": "success",
            "input": {},
            "output": {},
            "stateBefore": {},
            "stateAfter": {},
        }
        event = Event.model_validate(data)
        assert event.conversation_id == "conv-789"
        assert event.node_type == NodeType.TOOL

    def test_invalid_node_type_rejected(self):
        with pytest.raises(Exception):
            self._make_event(node_type="invalid")

    def test_invalid_status_rejected(self):
        with pytest.raises(Exception):
            self._make_event(status="unknown")

    def test_negative_latency_rejected(self):
        with pytest.raises(Exception):
            self._make_event(latency_ms=-100)

    def test_default_empty_dicts(self):
        event = self._make_event(input={}, output={}, state_before={}, state_after={})
        assert event.input == {}
        assert event.output == {}
        assert event.state_before == {}
        assert event.state_after == {}
