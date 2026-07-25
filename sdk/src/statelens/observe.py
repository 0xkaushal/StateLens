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
from statelens.storage import AsyncSQLiteStorage, SQLiteStorage


def observe(graph: Any, *, conversation_id: str | None = None, async_storage: bool = True) -> Any:
    """Instrument a LangGraph compiled graph for debugging.

    Attaches a StateLens callback handler to the graph so every node
    execution is captured and stored in the local SQLite database.

    Args:
        graph: A compiled LangGraph graph (CompiledGraph).
        conversation_id: Optional fixed conversation ID. If not provided,
            a new UUID is generated for each invocation.
        async_storage: If True (default), uses a non-blocking storage backend
            that offloads SQLite writes to a background thread. This prevents
            ainvoke()/astream() from being blocked by disk I/O. Set to False
            to use synchronous storage (simpler, slightly lower latency for
            sync invoke() usage).

    Returns:
        A wrapped graph that behaves identically but records events.

    Example:
        from statelens import observe

        app = graph.compile()
        app = observe(app)
        result = app.invoke({"messages": [...]})

        # Also works with async:
        result = await app.ainvoke({"messages": [...]})
    """
    if not FEATURES["langgraph"]:
        # Feature disabled — return graph unmodified
        return graph

    # Use async storage by default so ainvoke/astream don't block.
    # The async storage wraps sync SQLite in a thread pool.
    if async_storage:
        storage = AsyncSQLiteStorage()
    else:
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
    original_astream = getattr(graph, "astream", None)

    def wrapped_invoke(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return original_invoke(input, config=config, **kwargs)

    async def wrapped_ainvoke(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return await original_ainvoke(input, config=config, **kwargs)

    def wrapped_stream(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        return original_stream(input, config=config, **kwargs)

    async def wrapped_astream(input: Any, config: dict | None = None, **kwargs: Any) -> Any:
        config = _inject_handler(config, handler)
        async for chunk in original_astream(input, config=config, **kwargs):
            yield chunk

    graph.invoke = wrapped_invoke

    if original_ainvoke is not None:
        graph.ainvoke = wrapped_ainvoke

    if original_stream is not None:
        graph.stream = wrapped_stream

    if original_astream is not None:
        graph.astream = wrapped_astream

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
