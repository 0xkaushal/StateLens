"""StateLens Server — Configuration Settings."""

import os
from pathlib import Path


# Database
DB_PATH = Path(os.environ.get("STATELENS_DB_PATH", Path.home() / ".statelens" / "statelens.db"))

# Server
HOST = os.environ.get("STATELENS_HOST", "127.0.0.1")
PORT = int(os.environ.get("STATELENS_PORT", "8000"))

# CORS — allow Next.js dev server by default
CORS_ORIGINS = os.environ.get(
    "STATELENS_CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
).split(",")
