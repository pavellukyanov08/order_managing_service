import logging
from uuid import UUID
from redis.asyncio import Redis

from app.models import Order
from app.models.token import Token


class RedisAdapter:
    def __init__(
        self, *, logger: logging.Logger, redis_client: Redis
    ) -> None:
        self._logger = logger
        self._redis_client = redis_client

    async def get_order(
        self,
        order_id: int
    ) -> Order:
        pattern = Order.build_redis_key(sid=token_sid)
        token_model = None

        try:
            token_key = None
            async for key in self._redis_client.scan_iter(match=pattern):
                token_key = key
                break

            if token_key is None:
                return token_model

            token_model_json = await self._redis_client.get(name=token_key)
            if token_model_json is None:
                return token_model

            token_model = Token.model_validate_json(
                json_data=token_model_json
            )

            self._logger.info(
                "Received token for token_sid=%s",
                token_sid,
            )

    async def get_token(
        self,
        *,
        token_sid: UUID,
    ) -> Token | None:
        pattern = Token.build_redis_key(sid=token_sid)
        token_model = None

        try:
            token_key = None
            async for key in self._redis_client.scan_iter(match=pattern):
                token_key = key
                break

            if token_key is None:
                return token_model

            token_model_json = await self._redis_client.get(name=token_key)
            if token_model_json is None:
                return token_model

            token_model = Token.model_validate_json(
                json_data=token_model_json
            )

            self._logger.info(
                "Received token for token_sid=%s",
                token_sid,
            )
        except Exception as e:
            self._logger.error(
                "Failed to receive token: token_sid=%s error=%s",
                token_sid,
                e,
            )
            raise

        return token_model

    async def create_token_pair(
        self,
        *,
        access_token: Token,
        refresh_token: Token,
    ) -> None:
        access_token_serialize, refresh_token_serialize \
            = access_token.model_dump_json(), refresh_token.model_dump_json()

        try:
            await self._redis_client.set(
                name=refresh_token.redis_key,
                value=access_token_serialize,
            )
            await self._redis_client.expireat(
                name=refresh_token.redis_key,
                when=access_token.expired_at,
            )

            await self._redis_client.set(
                name=refresh_token.redis_key,
                value=refresh_token_serialize,
            )
            await self._redis_client.expireat(
                name=refresh_token.redis_key,
                when=refresh_token.expired_at,
            )

            self._logger.info(
                "Created token pair for token_sub=%s",
                refresh_token.token_sub,
            )
        except Exception as e:
            self._logger.error(
                "Failed to create token pair: "
                "token_sub=%s error=%s",
                refresh_token.token_sub,
                e,
            )
            raise

    async def remove_token_pair(
        self,
        *,
        token_sub: UUID,
    ) -> None:
        pattern = Token.build_redis_key(
            token_sub=token_sub
        )
        keys_to_remove = []

        try:
            async for key in self._redis_client.scan_iter(match=pattern):
                keys_to_remove.append(key)

            if keys_to_remove:
                await self._redis_client.delete(*keys_to_remove)
                self._logger.info(
                    "Removed %d token in token pair for pattern %s",
                    len(keys_to_remove),
                    pattern,
                )
            else:
                self._logger.warning(
                    "There are no tokens for removing pair by pattern %s",
                    pattern,
                )
        except Exception as e:
            self._logger.error(
                "Failed to remove token pair: pattern=%s error=%s",
                pattern,
                e,
            )
            raise

    async def remove_all_tokens(
        self,
        *,
        token_sub: UUID,
    ) -> None:
        pattern = Token.construct_redis_key(
            token_sub=token_sub
        )
        keys_to_remove = []

        try:
            async for key in self._redis_client.scan_iter(match=pattern):
                keys_to_remove.append(key)

            if keys_to_remove:
                await self._redis_client.delete(*keys_to_remove)
                self._logger.info(
                    "Removed all %d tokens for pattern %s",
                    len(keys_to_remove),
                    pattern,
                )
            else:
                self._logger.warning(
                    "There are no tokens for removing by pattern %s",
                    pattern,
                )
        except Exception as e:
            self._logger.error(
                "Failed to remove all tokens: pattern=%s error=%s",
                pattern,
                e,
            )
            raise