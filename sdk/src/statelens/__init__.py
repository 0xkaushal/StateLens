"""StateLens — Chrome DevTools for AI Agents.

Usage:
    from statelens import observe

    app = graph.compile()
    app = observe(app)
    result = app.invoke({"messages": [...]})
"""

from statelens.observe import observe

__all__ = ["observe"]
__version__ = "0.1.0"
