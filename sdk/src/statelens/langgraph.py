"""StateLens SDK — LangGraph Callback Handler.

Custom callback handler that hooks into LangGraph's execution lifecycle.
Captures node start/end, state transitions, and errors.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from statelens.collector import Collector
from statelens.events import EventStatus, NodeType

# LangGraph imports are optional — only needed when FEATURE_LANGGRAPH is enabled.
try:
    from langchain_core.callbacks import BaseCallbackHandler
except ImportError:
    # If langchain-core isn't installed, provide a stub base class
    # so the module can still be imported (feature-gated).
    class BaseCallbackHandler:  # type: ignore[no-redef]
        """Stub when langchain-core is not installed."""


def _infer_node_type(name: str, metadata: dict | None = None) -> NodeType:
    """Infer the node type from its name and metadata.

    Uses simple heuristics — can be extended as we learn more patterns.
    """
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
        run_id_str = str(run_id)
        name = serialized.get("name", "") or kwargs.get("name", "unknown")

        self._in_flight[run_id_str] = {
            "start_time": datetime.now(UTC),
            "name": name,
            "input": inputs if isinstance(inputs, dict) else {"value": inputs},
            "state_before": inputs.copy() if isinstance(inputs, dict) else {},
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
            return

        end_time = datetime.now(UTC)
        output_data = outputs if isinstance(outputs, dict) else {"value": outputs}

        self._collector.record_event(
            node_name=flight["name"],
            node_type=_infer_node_type(flight["name"], flight.get("metadata")),
            start_time=flight["start_time"],
            end_time=end_time,
            input_data=flight["input"],
            output_data=output_data,
            state_before=flight["state_before"],
            state_after=output_data.copy(),
            status=EventStatus.SUCCESS,
        )

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
            error=str(error),
        )

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
        name = serialized.get("name", "tool")

        self._in_flight[run_id_str] = {
            "start_time": datetime.now(UTC),
            "name": name,
            "input": inputs or {"query": input_str},
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
        output_data = output if isinstance(output, dict) else {"result": str(output)}

        self._collector.record_event(
            node_name=flight["name"],
            node_type=NodeType.TOOL,
            start_time=flight["start_time"],
            end_time=end_time,
            input_data=flight["input"],
            output_data=output_data,
            state_before=flight["state_before"],
            state_after=output_data.copy(),
            status=EventStatus.SUCCESS,
        )

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
            error=str(error),
        )
