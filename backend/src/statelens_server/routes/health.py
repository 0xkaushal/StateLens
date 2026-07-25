"""StateLens Server — Health Route."""

from fastapi import APIRouter

from statelens_server.schemas.responses import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()
