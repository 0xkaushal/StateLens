"""StateLens SDK — Feature Flags.

Single source of truth for all SDK feature flags.
Never access environment variables directly outside this file.
"""

import os


def _flag(name: str, default: bool = False) -> bool:
    """Read a boolean feature flag from environment."""
    value = os.environ.get(name, str(default).lower())
    return value.lower() in ("true", "1", "yes")


FEATURES: dict[str, bool] = {
    "langgraph": _flag("FEATURE_LANGGRAPH", default=True),
    "sqlite_storage": _flag("FEATURE_SQLITE_STORAGE", default=True),
    "openai_agents": _flag("FEATURE_OPENAI_AGENTS", default=False),
    "mcp": _flag("FEATURE_MCP", default=False),
    "crewai": _flag("FEATURE_CREWAI", default=False),
    "mastra": _flag("FEATURE_MASTRA", default=False),
}
