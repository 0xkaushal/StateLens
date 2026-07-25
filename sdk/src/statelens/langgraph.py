"""StateLens SDK — LangGraph Callback Handler.

Custom callback handler that hooks into LangGraph's execution lifecycle.
Captures node start/end, state transitions, and errors.

Hardened for:
- Nested/sub-graphs (only captures leaf nodes, skips wrapper chains)
- Serialization failures (gracefully degrades with empty dicts)
- Missing metadata / empty serialized dicts
- Non-dict inputs/outputs (wraps them safely)
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

from statelens.collector import Collector
from statelens.events import EventStatus, NodeType

logger = logging.getLogger("statelens")

# LangGraph imports are optional — only needed when FEATURE_LANGGRAPH is enabled.
try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    # If langchain-core isn't installed, provide a stub base class
    # so the module can still be imported (feature-gated).
    class BaseCallbackHandler:  # type: ignore[no-redef]
        """Stub when langchain-core is not installed."""


# Internal node names from LangGraph that represent graph-level wrappers,
# not actual user-defined nodes. We skip these to avoid noise.
_INTERNAL_NAMES = frozenset({
    "LangGraph",
    "RunnableSequence",
    "RunnableParallel",
    "RunnableLambda",
    "ChannelWrite",
    "ChannelRead",
    "__start__",
    "__end__",
})


def _safe_to_dict(value: Any) -> dict:
    """Safely convert a value to a JSON-serializable dict.

    Handles:
    - None → {}
    - Already a dict → returned as-is (shallow)
    - Has .dict() or .model_dump() (Pydantic) → call it
    - Strings/primitives → {"value": str(value)}
    - Non-serializable objects → {"_type": type_name, "_repr": repr}
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump()
        except Exception:
            pass
    if hasattr(value, "dict"):
        try:
            return value.dict()
        except Exception:
            pass
    if isinstance(value, (str, int, float, bool)):
        return {"value": value}
    if isinstance(value, (list, tuple)):
        return {"items": list(value)}

    # Last resort — try to make it representable
    try:
        json.dumps(value)
        return {"value": value}
    except (TypeError, ValueError):
        return {"_type": type(value).__name__, "_repr": repr(value)[:500]}


def _safe_copy(data: dict) -> dict:
    """Safely copy a dict for state snapshots.

    If the dict contains non-serializable values, returns a sanitized version.
    """
    try:
        # Fast path: if it's JSON-serializable, just copy it
        json.dumps(data)
        return data.copy()
    except (TypeError, ValueError):
        # Slow path: sanitize each value
        result = {}
        for key, value in data.items():
            try:
                json.dumps(value)
                result[key] = value
            except (TypeError, ValueError):
                result[key] = repr(value)[:200]
        return result


def _infer_node_type(name: str, metadata: dict | None = None) -> NodeType:
    """Infer the node type from its name and metadata.

    Priority:
    1. Explicit 'langgraph_node_type' in metadata (set by some custom nodes)
    2. Name-based heuristics
    3. Default to LLM
    """
    # Check metadata first (explicit override)
    if metadata:
        explicit_type = metadata.get("langgraph_node_type") or metadata.get("node_type")
        if explicit_type:
            try:
                return NodeType(explicit_type)
            except ValueError:
                pass  # Fall through to heuristics

    name_lower = name.lower()

    if any(kw in name_lower for kw in ("llm", "chat", "model", "agent")):
        return NodeType.LLM
    if any(kw in name_lower for kw in ("tool", "search", "retrieve", "fetch")):
        return NodeType.TOOL
    if any(kw in name_lower for kw in ("memory", "store", "remember")):
        return NodeType.MEMORY
    if any(kw in name_lower for kw in ("plan", "think", "reason")):
        return NodeType.PLANNER
    if any(kw in name_lower for kw in ("route", "router", "branch", "condition")):
        return NodeType.ROUTER

    # Default to LLM if we can't infer
    return NodeType.LLM


class StateLensCallbackHandler(BaseCallbackHandler):
    """LangGraph callback handler that captures execution events for StateLens.

    Handles edge cases:
    - Nested graphs: skips internal wrapper nodes (_INTERNAL_NAMES)
    - Serialization: gracefully handles non-serializable inputs/outputs
    - Missing data: never crashes on None/empty metadata
    - Orphaned ends: if on_chain_end arrives without a matching start, it's ignored

    Usage:
        handler = StateLensCallbackHandler(collector)
        graph.invoke(input, config={"callbacks": [handler]})
    """

    def __init__(self, collector: Collector) -> None:
        self._collector = collector
        # Track in-flight node executions: run_id -> {start_time, name, input, state}
        self._in_flight: dict[str, dict[str, Any]] = {}

    @property
    def collector(self) -> Collector:
        return self._collector

    def _is_internal_node(self, name: str) -> bool:
        """Check if this is an internal LangGraph wrapper node we should skip."""
        return name in _INTERNAL_NAMES or name.startswith("__")

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a LangGraph node starts execution."""
        name = (serialized or {}).get("name", "") or kwargs.get("name", "unknown")

        # Skip internal wrapper nodes
        if self._is_internal_node(name):
            return

        run_id_str = str(run_id)
        input_data = _safe_to_dict(inputs)

        self._in_flight[run_id_str] = {
            "start_time": datetime.now(UTC),
            "name": name,
            "input": input_data,
            "state_before": _safe_copy(input_data),
            "metadata": metadata or {},
        }

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a LangGraph node finishes execution."""
        run_id_str = str(run_id)
        flight = self._in_flight.pop(run_id_str, None)
        if flight is None:
            return  # Orphaned end (internal node or missed start) — skip

        end_time = datetime.now(UTC)
        output_data = _safe_to_dict(outputs)

        try:
            self._collector.record_event(
                node_name=flight["name"],
                node_type=_infer_node_type(flight["name"], flight.get("metadata")),
                start_time=flight["start_time"],
                end_time=end_time,
                input_data=flight["input"],
                output_data=output_data,
                state_before=flight["state_before"],
                state_after=_safe_copy(output_data),
                status=EventStatus.SUCCESS,
            )
        except Exception as e:
            logger.warning(f"StateLens: failed to record event for '{flight['name']}': {e}")

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a LangGraph node raises an exception."""
        run_id_str = str(run_id)
        flight = self._in_flight.pop(run_id_str, None)
        if flight is None:
            return

        end_time = datetime.now(UTC)

        try:
            self._collector.record_event(
                node_name=flight["name"],
                node_type=_infer_node_type(flight["name"], flight.get("metadata")),
                start_time=flight["start_time"],
                end_time=end_time,
                input_data=flight["input"],
                output_data={},
                state_before=flight["state_before"],
                state_after={},
                status=EventStatus.FAILED,
                error=str(error)[:2000],  # Truncate very long error messages
            )
        except Exception as e:
            logger.warning(f"StateLens: failed to record error event for '{flight['name']}': {e}")

    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool starts execution."""
        run_id_str = str(run_id)
        name = (serialized or {}).get("name", "tool")

        input_data = _safe_to_dict(inputs) if inputs else {"query": str(input_str)[:1000]}

        self._in_flight[run_id_str] = {
            "start_time": datetime.now(UTC),
            "name": name,
            "input": input_data,
            "state_before": {},
            "metadata": metadata or {},
        }

    def on_tool_end(
        self,
        output: str | Any,
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool finishes execution."""
        run_id_str = str(run_id)
        flight = self._in_flight.pop(run_id_str, None)
        if flight is None:
            return

        end_time = datetime.now(UTC)
        output_data = _safe_to_dict(output)

        try:
            self._collector.record_event(
                node_name=flight["name"],
                node_type=NodeType.TOOL,
                start_time=flight["start_time"],
                end_time=end_time,
                input_data=flight["input"],
                output_data=output_data,
                state_before=flight["state_before"],
                state_after=_safe_copy(output_data),
                status=EventStatus.SUCCESS,
            )
        except Exception as e:
            logger.warning(f"StateLens: failed to record tool event for '{flight['name']}': {e}")

    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: str | Any,
        parent_run_id: str | Any | None = None,
        **kwargs: Any,
    ) -> None:
        """Called when a tool raises an exception."""
        run_id_str = str(run_id)
        flight = self._in_flight.pop(run_id_str, None)
        if flight is None:
            return

        end_time = datetime.now(UTC)

        try:
            self._collector.record_event(
                node_name=flight["name"],
                node_type=NodeType.TOOL,
                start_time=flight["start_time"],
                end_time=end_time,
                input_data=flight["input"],
                output_data={},
                state_before=flight["state_before"],
                state_after={},
                status=EventStatus.FAILED,
                error=str(error)[:2000],
            )
        except Exception as e:
            logger.warning(f"StateLens: failed to record tool error for '{flight['name']}': {e}")
