"""StateLens Server — Event Routes."""

from fastapi import APIRouter

from statelens_server.schemas.responses import EventResponse
from statelens_server.services.event_service import get_events

router = APIRouter()


@router.get("/events/{conversation_id}", response_model=list[EventResponse])
def get_conversation_events(conversation_id: str) -> list[EventResponse]:
    """Get all events for a conversation, ordered by start time."""
    return get_events(conversation_id)
