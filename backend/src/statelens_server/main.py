"""StateLens Server — FastAPI Application.

Entry point for the backend server.
Serves both the REST API and the bundled frontend UI.

Run with: statelens
Or:       uvicorn statelens_server.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from statelens_server.config import CORS_ORIGINS, HOST, PORT
from statelens_server.database.connection import db
from statelens_server.routes import conversations_router, events_router, health_router

# Path to the bundled frontend static files
STATIC_DIR = Path(__file__).parent / "static"


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

    # Register API routes
    app.include_router(health_router)
    app.include_router(conversations_router)
    app.include_router(events_router)

    # Serve bundled frontend UI
    if STATIC_DIR.exists():
        # Serve static assets (JS, CSS, images) under /_next/
        next_dir = STATIC_DIR / "_next"
        if next_dir.exists():
            app.mount("/_next", StaticFiles(directory=str(next_dir)), name="next-static")

        # Serve the index.html for the root path
        @app.get("/", include_in_schema=False)
        async def serve_ui():
            return FileResponse(str(STATIC_DIR / "index.html"))

        # Serve the landing page
        @app.get("/landing", include_in_schema=False)
        async def serve_landing():
            landing_html = STATIC_DIR / "landing.html"
            if landing_html.exists():
                return FileResponse(str(landing_html))
            return FileResponse(str(STATIC_DIR / "index.html"))

    return app


# Module-level app instance for uvicorn
app = create_app()


def run() -> None:
    """CLI entry point for `statelens` command."""
    import webbrowser

    print("🔍 StateLens — Chrome DevTools for AI Agents")
    print(f"   Starting server at http://{HOST}:{PORT}")
    print(f"   Open http://{HOST}:{PORT} in your browser")
    print()

    # Open browser automatically
    webbrowser.open(f"http://{HOST}:{PORT}")

    uvicorn.run(
        "statelens_server.main:app",
        host=HOST,
        port=PORT,
        reload=False,
    )
