from datetime import datetime
from uuid import UUID

from pydantic import Field, BaseModel
from app.enums import TokenTypeEnum
from app.utils import NormalizeDateTime


class TokenPair(BaseModel):
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")


class TokenPayload(NormalizeDateTime):
    token_sub: UUID = Field(..., description="Token owner (user_sid)")
    token_type: TokenTypeEnum = Field(..., description="Token type")
    jti: UUID = Field(..., description="Token unique id")
    expired_at: datetime = Field(..., description="Token expired at")
    created_at: datetime = Field(..., description="Token created at")


class RefreshToken(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")


class CreateTokenPair(BaseModel):
    sub: UUID = Field(..., description="Token owner (user_sid)")

