from typing import Annotated
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis as RedisClient

from app.common.adapters import PostgresAdapter, RedisAdapter
from app.core.database import get_db
from app.utils.logger import LoggerDep


def _get_common_postgres_adapter(
    logger: LoggerDep,
    postgres_session: Annotated[AsyncSession, Depends(get_db)],
) -> PostgresAdapter:
    return PostgresAdapter(
        logger=logger,
        postgres_session=postgres_session
    )


def get_redis_client(request: Request) -> RedisClient:
    redis_client: RedisClient | None = getattr(
        request.app.state, "redis_client", None
    )
    if not redis_client:
        raise RuntimeError("Missing required app state: redis_client")
    return redis_client


def _get_common_redis_adapter(
    logger: LoggerDep,
    redis_client: Annotated[RedisClient, Depends(get_redis_client)]
) -> RedisAdapter:
    return RedisAdapter(logger=logger, redis_client=redis_client)


CommonRedisDep = Annotated[RedisAdapter, Depends(_get_common_redis_adapter)]
CommonPostgresDep = Annotated[PostgresAdapter, Depends(_get_common_postgres_adapter)]
