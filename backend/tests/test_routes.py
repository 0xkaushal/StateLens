"""Tests for statelens_server — API route tests using FastAPI TestClient."""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from statelens_server.main import create_app
from statelens_server.database.connection import Database


@pytest.fixture
def test_db(tmp_path):
    """Create a test database with sample data."""
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("""
        CREATE TABLE events (
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
    conn.execute("""
        INSERT INTO events VALUES (
            'node-001', 'conv-001', 'planner', 'planner',
            '2025-07-25T10:00:00Z', '2025-07-25T10:00:01Z', 1000,
            'success', '{"messages": [{"role": "user", "content": "What is the weather?"}]}', '{"a": "plan"}', '{}', '{"step": 1}', NULL
        )
    """)
    conn.execute("""
        INSERT INTO events VALUES (
            'node-002', 'conv-001', 'search_tool', 'tool',
            '2025-07-25T10:00:01Z', '2025-07-25T10:00:03Z', 2000,
            'success', '{"query": "test"}', '{"result": "found"}', '{"step": 1}', '{"step": 2}', NULL
        )
    """)
    conn.execute("""
        INSERT INTO events VALUES (
            'node-003', 'conv-002', 'agent', 'llm',
            '2025-07-25T09:00:00Z', '2025-07-25T09:00:05Z', 5000,
            'failed', '{}', '{}', '{}', '{}', 'LLM timeout'
        )
    """)
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def client(test_db):
    """Create a test client with the test database."""
    with patch("statelens_server.config.settings.DB_PATH", test_db):
        app = create_app()
        # Manually connect the database for the test
        from statelens_server.database.connection import db
        db._db_path = test_db
        db.connect()
        yield TestClient(app)
        db.close()


class TestHealthRoute:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"


class TestConversationsRoute:
    def test_list_conversations(self, client):
        response = client.get("/conversations")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_conversations_ordered_by_most_recent(self, client):
        response = client.get("/conversations")
        data = response.json()
        # conv-001 ends at 10:00:03, conv-002 ends at 09:00:05
        assert data[0]["id"] == "conv-001"
        assert data[1]["id"] == "conv-002"

    def test_conversation_summary_fields(self, client):
        response = client.get("/conversations")
        data = response.json()
        conv = data[0]  # conv-001
        assert conv["id"] == "conv-001"
        assert conv["totalEvents"] == 2
        assert conv["totalLatencyMs"] == 3000.0
        assert conv["status"] == "success"
        assert "createdAt" in conv
        assert "updatedAt" in conv
        assert "title" in conv

    def test_failed_conversation_status(self, client):
        response = client.get("/conversations")
        data = response.json()
        conv = data[1]  # conv-002
        assert conv["status"] == "failed"

    def test_get_conversation_detail(self, client):
        response = client.get("/conversations/conv-001")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "conv-001"
        assert data["totalEvents"] == 2
        assert len(data["events"]) == 2
        assert "title" in data

    def test_get_conversation_not_found(self, client):
        response = client.get("/conversations/nonexistent")
        assert response.status_code == 404
        assert response.json()["detail"] == "Conversation not found"


class TestEventsRoute:
    def test_get_events(self, client):
        response = client.get("/events/conv-001")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_events_ordered_by_start_time(self, client):
        response = client.get("/events/conv-001")
        data = response.json()
        assert data[0]["nodeName"] == "planner"
        assert data[1]["nodeName"] == "search_tool"

    def test_event_fields(self, client):
        response = client.get("/events/conv-001")
        data = response.json()
        event = data[0]
        assert event["conversationId"] == "conv-001"
        assert event["nodeId"] == "node-001"
        assert event["nodeName"] == "planner"
        assert event["nodeType"] == "planner"
        assert event["latencyMs"] == 1000
        assert event["status"] == "success"
        assert event["input"] == {"messages": [{"role": "user", "content": "What is the weather?"}]}
        assert event["output"] == {"a": "plan"}
        assert event["error"] is None

    def test_event_with_error(self, client):
        response = client.get("/events/conv-002")
        data = response.json()
        assert data[0]["status"] == "failed"
        assert data[0]["error"] == "LLM timeout"

    def test_events_empty_conversation(self, client):
        response = client.get("/events/nonexistent")
        assert response.status_code == 200
        data = response.json()
        assert data == []


class TestCORS:
    def test_cors_headers_present(self, client):
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert "access-control-allow-origin" in response.headers
