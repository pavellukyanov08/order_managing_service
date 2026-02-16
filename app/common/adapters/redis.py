from uuid import UUID
from redis.asyncio import Redis as RedisClient

from app.utils import LoggerDep
from app.schemas import OrderRead
from app.models.token import Token


class RedisAdapter:
    def __init__(
        self, *, logger: LoggerDep, redis_client: RedisClient
    ) -> None:
        self._logger = logger
        self._redis_client = redis_client

    async def get_order(
        self,
        order_id: int
    ) -> OrderRead | None:
        order_key = f"order: {order_id}"

        try:
            order_json = await self._redis_client.get(name=order_key)
            if order_json:
                order = OrderRead.model_validate_json(order_json)
                self._logger.info("Order %d found", order_id)
                return order

            self._logger.info(
                "Order %d not found in cache",
                order_id,
            )
        except Exception as e:
            self._logger.error("Failed while searching order=%d", order_id, e)
            return None

    async def set_order(self, order_id: int, order: OrderRead) -> None:
        redis_key = f"order:{order_id}"
        order_json = order.model_dump_json(exclude={"redis_key"})

        try:
            await self._redis_client.set(redis_key, order_json, ex=600)
            self._logger.info("Order %d cached for 10 min", order_id)
        except Exception as e:
            self._logger.error("Redis SET order %d failed: %s", order_id, e)
            raise

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
                name=access_token.redis_key,
                value=access_token_serialize,
            )
            await self._redis_client.expireat(
                name=access_token.redis_key,
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

    async def revoke_token_pair(
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
                    "%d tokens have been revoked by %s",
                    len(keys_to_remove),
                    pattern,
                )
            else:
                self._logger.warning(
                    "There are no tokens for revoking by pattern %s",
                    pattern,
                )
        except Exception as e:
            self._logger.error(
                "Failed to revoked token=%d error=%s",
                pattern,
                e,
            )
            raise