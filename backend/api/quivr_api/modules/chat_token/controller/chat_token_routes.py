from fastapi import APIRouter, Depends, HTTPException

from quivr_api.logger import get_logger
from quivr_api.middlewares.auth import AuthBearer, get_current_user
from quivr_api.modules.brain.service.brain_user_service import BrainUserService
from quivr_api.modules.chat_token.entity.chat_token import (
    ChatTokenRequest,
    ChatTokenResponse,
)
from quivr_api.modules.chat_token.service.chat_token_service import chat_token_service
from quivr_api.modules.user.entity.user_identity import UserIdentity

logger = get_logger(__name__)

router = APIRouter()
brain_user_service = BrainUserService()


@router.post(
    "/chat/token",
    response_model=ChatTokenResponse,
    summary="Create a scoped chat token",
    description="""
    Creates a time-limited, brain-scoped token for chat operations.

    This endpoint is designed for integrations (like Moodle) where:
    - The backend holds the master API key
    - Frontend receives a scoped token with limited validity
    - Token can only be used to chat with the specified brain

    The token expires after the specified TTL (default: 10 minutes).
    """,
    dependencies=[Depends(AuthBearer())],
    tags=["Chat Token"],
)
async def create_chat_token(
    request: ChatTokenRequest,
    current_user: UserIdentity = Depends(get_current_user),
) -> ChatTokenResponse:
    """
    Create a scoped chat token for a specific brain.

    Requires the user to have access to the brain.
    """
    # Verify user has access to the brain
    user_brain = brain_user_service.get_brain_for_user(
        current_user.id, request.brain_id
    )

    if not user_brain:
        logger.warning(
            f"User {current_user.id} attempted to create chat token for "
            f"brain {request.brain_id} without access"
        )
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this brain",
        )

    # Limit TTL to reasonable values (1-60 minutes)
    ttl_minutes = max(1, min(60, request.ttl_minutes))

    return chat_token_service.create_chat_token(
        user_id=current_user.id,
        brain_id=request.brain_id,
        ttl_minutes=ttl_minutes,
    )
