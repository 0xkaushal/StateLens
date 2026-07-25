"""StateLens Server — FastAPI Application.

Entry point for the backend server.
Run with: uvicorn statelens_server.main:app --reload
Or:       statelens-server (if installed via pip)
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from statelens_server.config import CORS_ORIGINS, HOST, PORT
from statelens_server.database.connection import db
from statelens_server.routes import conversations_router, events_router, health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application lifecycle — connect/disconnect database."""
    db.connect()
    yield
    db.close()


def create_app() -> FastAPI:
    """Application factory — creates and configures the FastAPI app."""
    app = FastAPI(
        title="StateLens",
        description="Chrome DevTools for AI Agents — Debug API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # CORS — allow the Next.js frontend dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    # Register routes
    app.include_router(health_router)
    app.include_router(conversations_router)
    app.include_router(events_router)

    return app


# Module-level app instance for uvicorn
app = create_app()


def run() -> None:
    """CLI entry point for statelens-server command."""
    uvicorn.run(
        "statelens_server.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
