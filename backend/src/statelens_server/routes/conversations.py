"""StateLens Server — Conversation Routes."""

from fastapi import APIRouter, HTTPException

from statelens_server.schemas.responses import ConversationDetail, ConversationSummary
from statelens_server.services.conversation_service import (
    get_conversation,
    list_conversations,
)

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummary])
def get_conversations() -> list[ConversationSummary]:
    """List all conversations, most recent first."""
    return list_conversations()


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
@router.get("/conversation/{conversation_id}", response_model=ConversationDetail, include_in_schema=False)
def get_conversation_detail(conversation_id: str) -> ConversationDetail:
    """Get a single conversation with all its events."""
    conversation = get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
