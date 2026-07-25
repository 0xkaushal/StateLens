"""Tests for statelens_server.config — Feature flags and settings."""

import os
from unittest.mock import patch

import pytest


class TestFeatureFlags:
    def test_default_flags(self):
        from statelens_server.config.features import FEATURES

        assert FEATURES["langgraph"] is True
        assert FEATURES["sqlite_storage"] is True
        assert FEATURES["prompt_diff"] is False
        assert FEATURES["root_cause_analysis"] is False
        assert FEATURES["mcp"] is False

    def test_flag_reads_env_true(self, monkeypatch):
        monkeypatch.setenv("FEATURE_PROMPT_DIFF", "true")
        # Re-import to pick up new env
        from statelens_server.config.features import _flag
        assert _flag("FEATURE_PROMPT_DIFF", default=False) is True

    def test_flag_reads_env_false(self, monkeypatch):
        monkeypatch.setenv("FEATURE_LANGGRAPH", "false")
        from statelens_server.config.features import _flag
        assert _flag("FEATURE_LANGGRAPH", default=True) is False

    def test_flag_accepts_1_as_true(self, monkeypatch):
        monkeypatch.setenv("FEATURE_MCP", "1")
        from statelens_server.config.features import _flag
        assert _flag("FEATURE_MCP", default=False) is True


class TestSettings:
    def test_default_host(self, monkeypatch):
        monkeypatch.delenv("STATELENS_HOST", raising=False)
        # Force reimport
        import importlib
        import statelens_server.config.settings as settings
        importlib.reload(settings)
        assert settings.HOST == "127.0.0.1"

    def test_default_port(self, monkeypatch):
        monkeypatch.delenv("STATELENS_PORT", raising=False)
        import importlib
        import statelens_server.config.settings as settings
        importlib.reload(settings)
        assert settings.PORT == 8000

    def test_custom_port(self, monkeypatch):
        monkeypatch.setenv("STATELENS_PORT", "9000")
        import importlib
        import statelens_server.config.settings as settings
        importlib.reload(settings)
        assert settings.PORT == 9000
