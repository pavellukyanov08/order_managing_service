import logging
from datetime import timedelta
from uuid import UUID, uuid4

from fastapi import HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

from app.common.adapters import RedisAdapter
from app.core import jwt_auth
from app.enums import TokenTypeEnum
from app.models import Token
from app.settings import jwt_settings
from app.utils import DateTimeManager
from app.utils.crypto_manager import get_hash_sha256
from app.schemas import CreateTokenPair, TokenPair, TokenPayload, RefreshToken


class TokenService:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        redis_adapter: RedisAdapter,
    ) -> None:
        self._logger = logger
        self._redis_adapter = redis_adapter
        self._tokens_ttl= {
            TokenTypeEnum.ACCESS: jwt_settings.jwt_access_token_ttl,
            TokenTypeEnum.REFRESH: jwt_settings.jwt_refresh_token_ttl,
        }
        self._token_types_errors = {
            TokenTypeEnum.ACCESS: HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid access token",
            ),
            TokenTypeEnum.REFRESH: HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            ),
        }

    @staticmethod
    def _get_token_model(
        *,
        token: str,
        token_payload: TokenPayload,
    ) -> Token:
        token_hash = get_hash_sha256(data=token)
        return Token(
            sid=token_payload.jti,
            hash=token_hash,
            token_sub=token_payload.token_sub,
            token_type=token_payload.token_type,
            expired_at=token_payload.expired_at,
            created_at=token_payload.created_at,
        )

    async def check_token(
        self,
        *,
        token: str,
        token_type: TokenTypeEnum,
    ) -> Token:
        try:
            decoded_payload = jwt_auth.decode_token(token=token)
        except Exception as e:
            self._logger.error("Failed to decode token: error=%s", e)
            raise self._token_types_errors.get(token_type, HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            ))
        
        if decoded_payload.get('token_type') != token_type:
            raise self._token_types_errors.get(token_type, HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            ))
        
        token_sid = decoded_payload.get('jti')
        if not token_sid:
            raise self._token_types_errors.get(token_type, HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            ))
        
        token_model = await self._redis_adapter.get_token(token_sid=token_sid)
        if token_model is None:
            raise self._token_types_errors.get(token_type, HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token not found or expired"
            ))
        
        if token_model.hash != get_hash_sha256(data=token):
            raise self._token_types_errors.get(token_type, HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Token hash mismatch"
            ))

        return token_model

    def get_token_with_payload(
        self,
        *,
        token_sub: UUID,
        token_type: TokenTypeEnum,
    ) -> tuple[str, TokenPayload]:
        created_at = DateTimeManager.get_now_utc()
        payload = TokenPayload(
            token_sub=token_sub,
            token_type=token_type,
            jti=uuid4(),
            created_at=DateTimeManager.get_now_utc(),
            expired_at=created_at + timedelta(
                seconds=self._tokens_ttl.get(token_type, 0)
            ),
        )
        token = jwt_auth.encode_token(
            payload=payload.model_dump(mode="json"),
            expire_minutes=payload.expired_at,
        )
        return token, payload

    def _get_token_with_model(
        self,
        *,
        token_sub: UUID,
        token_type: TokenTypeEnum,
    ) -> tuple[str, Token]:
        token, token_payload = self.get_token_with_payload(
            token_sub=token_sub,
            token_type=token_type,
        )
        token_model = self._get_token_model(
            token=token,
            token_payload=token_payload,
        )
        return token, token_model

    async def create_token_pair(
        self,
        *,
        data: CreateTokenPair,
    ) -> TokenPair:
        access_token, access_token_model = self._get_token_with_model(
            token_sub=data.sub,
            token_type=TokenTypeEnum.ACCESS,
        )
        refresh_token, refresh_token_model = self._get_token_with_model(
            token_sub=data.sub,
            token_type=TokenTypeEnum.REFRESH,
        )
        await self.revoke_token_pair(
            token_sub=data.sub,
        )
        await self._redis_adapter.create_token_pair(
            access_token=access_token_model,
            refresh_token=refresh_token_model,
        )
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token
        )

    async def refresh_token_pair(
        self,
        *,
        data: RefreshToken,
    ) -> TokenPair:
        token_model = await self.check_token(
            token=data.refresh_token, token_type=TokenTypeEnum.REFRESH
        )
        access_token, access_token_model = self._get_token_with_model(
            token_sub=token_model.token_sub,
            token_type=TokenTypeEnum.ACCESS,
        )
        refresh_token, refresh_token_model = self._get_token_with_model(
            token_sub=token_model.token_sub,
            token_type=TokenTypeEnum.REFRESH,
        )
        await self.revoke_token_pair(
            token_sub=token_model.token_sub,
        )
        await self._redis_adapter.create_token_pair(
            access_token=access_token_model,
            refresh_token=refresh_token_model,
        )
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token
        )

    async def revoke_token_pair(
        self,
        *,
        token_sub: UUID,
    ) -> None:
        await self._redis_adapter.revoke_token_pair(
            token_sub=token_sub,
        )