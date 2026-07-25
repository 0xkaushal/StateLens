"""StateLens Server — Configuration Settings."""

import os
from pathlib import Path


def _resolve_db_path() -> Path:
    """Resolve database path: env var > project-local > home directory.

    Priority:
        1. STATELENS_DB_PATH environment variable (explicit override)
        2. .statelens/statelens.db in CWD (project-local, created by `statelens init`)
        3. ~/.statelens/statelens.db (home directory fallback)
    """
    env_path = os.environ.get("STATELENS_DB_PATH")
    if env_path:
        return Path(env_path)

    # Project-local: created by `statelens init`
    local_db = Path.cwd() / ".statelens" / "statelens.db"
    if local_db.parent.exists():
        return local_db

    return Path.home() / ".statelens" / "statelens.db"


# Database
DB_PATH = _resolve_db_path()

# Server
HOST = os.environ.get("STATELENS_HOST", "127.0.0.1")
PORT = int(os.environ.get("STATELENS_PORT", "8000"))

# CORS — allow the Next.js frontend dev server
CORS_ORIGINS = os.environ.get(
    "STATELENS_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")
