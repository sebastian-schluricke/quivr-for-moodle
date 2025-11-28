from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ChatTokenRequest(BaseModel):
    """Request body for creating a chat token"""
    brain_id: UUID
    ttl_minutes: int = 10  # Default 10 minutes


class ChatTokenResponse(BaseModel):
    """Response containing the chat token"""
    token: str
    brain_id: UUID
    expires_at: datetime


class ChatTokenPayload(BaseModel):
    """Payload decoded from a chat token JWT"""
    user_id: UUID
    brain_id: UUID
    token_type: str = "chat_token"
    exp: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.exp
