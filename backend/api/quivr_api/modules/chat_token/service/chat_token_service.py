import os
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from jose import jwt
from jose.exceptions import JWTError

from quivr_api.logger import get_logger
from quivr_api.modules.chat_token.entity.chat_token import (
    ChatTokenPayload,
    ChatTokenResponse,
)

logger = get_logger(__name__)

SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
ALGORITHM = "HS256"


class ChatTokenService:
    """Service for creating and verifying scoped chat tokens"""

    def create_chat_token(
        self,
        user_id: UUID,
        brain_id: UUID,
        ttl_minutes: int = 10,
    ) -> ChatTokenResponse:
        """
        Create a scoped chat token for a specific brain.

        Args:
            user_id: The user ID requesting the token
            brain_id: The brain ID this token is scoped to
            ttl_minutes: Token validity in minutes (default: 10)

        Returns:
            ChatTokenResponse with token, brain_id, and expiry
        """
        expires_at = datetime.utcnow() + timedelta(minutes=ttl_minutes)

        payload = {
            "sub": str(user_id),
            "brain_id": str(brain_id),
            "token_type": "chat_token",
            "exp": expires_at,
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

        logger.info(
            f"Created chat token for user {user_id} scoped to brain {brain_id}, "
            f"expires at {expires_at}"
        )

        return ChatTokenResponse(
            token=token,
            brain_id=brain_id,
            expires_at=expires_at,
        )

    def verify_chat_token(self, token: str) -> Optional[ChatTokenPayload]:
        """
        Verify a chat token and return its payload.

        Args:
            token: The JWT token string

        Returns:
            ChatTokenPayload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                options={"verify_aud": False},
            )

            # Check if this is a chat token
            if payload.get("token_type") != "chat_token":
                return None

            return ChatTokenPayload(
                user_id=UUID(payload["sub"]),
                brain_id=UUID(payload["brain_id"]),
                token_type=payload["token_type"],
                exp=datetime.fromtimestamp(payload["exp"]),
            )

        except JWTError as e:
            logger.debug(f"Chat token verification failed: {e}")
            return None
        except (KeyError, ValueError) as e:
            logger.debug(f"Chat token payload invalid: {e}")
            return None


# Singleton instance
chat_token_service = ChatTokenService()
