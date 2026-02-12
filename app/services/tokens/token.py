import logging
from datetime import timedelta
from uuid import UUID, uuid4

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

    def _get_token_payload(
        self, *, token: str
    ) -> TokenPayload:
        try:
            token_payload = jwt_auth.decode_token(token=token)
            return TokenPayload.model_validate(obj=token_payload)
        except Exception as e:
            self._logger.error("Failed to receive token payload: error=%s", e)
            raise

    async def _check_token(
        self,
        *,
        token: str,
    ) -> Token:
        token_payload = jwt_auth.decode_token(
            token=token
        )
        TokenPayload.model_validate(obj=token_payload)

        if token_payload.type != token_type:
            raise self._token_invalid_errors_map.get(token_type, "")
        if access_services and token_payload.service not in access_services:
            raise self._token_invalid_errors_map.get(token_type, "")
        token_model = await self._service.get_token(
            token_sid=token_payload.jti
        )
        if token_model is None or token_model.hash != self._get_token_hash(
            token=token
        ):
            raise self._token_invalid_errors_map.get(token_type, "")
        return token_model

    @staticmethod
    def get_token_with_payload(
        *,
        token_sub: UUID,
        token_type: TokenTypeEnum,
        expire_seconds=jwt_settings.jwt_access_token_ttl,
    ) -> tuple[str, TokenPayload]:
        created_at = DateTimeManager.get_now_utc()
        payload = TokenPayload(
            token_sub=token_sub,
            token_type=token_type,
            jti=uuid4(),
            created_at=DateTimeManager.get_now_utc(),
            expired_at=created_at + timedelta(seconds=expire_seconds),
        )
        token = jwt_auth.encode_token(
            payload=payload.model_dump(mode="json"),
            expire_minutes=jwt_settings.jwt_access_token_ttl,
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

    async def remove_token_pair(
        self,
        *,
        token_sub: UUID,
    ) -> None:
        await self._redis_adapter.remove_token_pair(
            token_sub=token_sub,
        )

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
        await self.remove_token_pair(
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
        token_model = self._check_token()
        access_token, access_token_model = self._get_token_with_model(
            token_sub=data.sub,
            token_type=TokenTypeEnum.ACCESS,
        )
        refresh_token, refresh_token_model = self._get_token_with_model(
            token_sub=data.sub,
            token_type=TokenTypeEnum.REFRESH,
        )
        await self.remove_token_pair(
            token_sub=data.sub,
        )
        await self._redis_adapter.create_token_pair(
            access_token=access_token_model,
            refresh_token=refresh_token_model,
        )
        return TokenPair(
            access_token=access_token, refresh_token=refresh_token
        )
