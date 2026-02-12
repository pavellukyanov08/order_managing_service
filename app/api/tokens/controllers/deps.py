from typing import Annotated
from fastapi import Depends

from app.services.tokens import TokenService
from app.common.deps import CommonRedisDep
from app.utils import LoggerDep


def _get_token_service(
    logger: LoggerDep,
    redis_adapter: CommonRedisDep,
) -> TokenService:
    return TokenService(
        logger=logger,
        redis_adapter=redis_adapter
    )

TokenServiceDep = Annotated[TokenService, Depends(_get_token_service)]
