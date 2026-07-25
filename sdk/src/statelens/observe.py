"""StateLens SDK — Public API.

The entry point for users:

    from statelens import observe
    graph = observe(graph)

That's it. Zero configuration needed.
"""

from __future__ import annotations

from typing import Any

from statelens.collector import Collector
from statelens.config import FEATURES
from statelens.langgraph import StateLensCallbackHandler
from statelens.storage import SQLiteStorage


def observe(graph: Any, *, conversation_id: str | None = None) -> Any:
    """Instrument a LangGraph compiled graph for debugging.

    Attaches a StateLens callback handler to the graph so every node
    execution is captured and stored in the local SQLite database.

    Args:
        graph: A compiled LangGraph graph (CompiledGraph).
        conversation_id: Optional fixed conversation ID. If not provided,
            a new UUID is generated for each invocation.

    Returns:
        A wrapped graph that behaves identically but records events.

    Example:
        from statelens import observe

        app = graph.compile()
        app = observe(app)
        result = app.invoke({"messages": [...]})
    """
    if not FEATURES["langgraph"]:
        # Feature disabled — return graph unmodified
        return graph

    storage = SQLiteStorage()
    collector = Collector(conversation_id=conversation_id, storage=storage)
    handler = StateLensCallbackHandler(collector)

    # Wrap the graph's invoke and ainvoke to inject our callback
    return _wrap_graph(graph, handler)


def _wrap_graph(graph: Any, handler: StateLensCallbackHandler) -> Any:
    """Wrap a compiled graph to inject the StateLens callback handler.

    Preserves all original graph behavior — just adds our handler
    to the callbacks list on every call.
    """
    original_invoke = graph.invoke
    original_ainvoke = getattr(graph, "ainvoke", None)
    original_stream = getattr(graph, "stream", None)

    def wrapped_invoke(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return original_invoke(input, config=config, **kwargs)

    async def wrapped_ainvoke(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return await original_ainvoke(input, config=config, **kwargs)

    def wrapped_stream(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return original_stream(input, config=config, **kwargs)

    graph.invoke = wrapped_invoke

    if original_ainvoke is not None:
        graph.ainvoke = wrapped_ainvoke

    if original_stream is not None:
        graph.stream = wrapped_stream

    # Attach collector for advanced usage (e.g. accessing conversation_id)
    graph._statelens_collector = handler.collector

    return graph


def _inject_handler(config: dict | None, handler: StateLensCallbackHandler) -> dict:
    """Inject our callback handler into the LangGraph config."""
    if config is None:
        config = {}
    else:
        config = config.copy()

    callbacks = config.get("callbacks", [])
    if not isinstance(callbacks, list):
        callbacks = list(callbacks)
    else:
        callbacks = callbacks.copy()

    callbacks.append(handler)
    config["callbacks"] = callbacks
    return config
