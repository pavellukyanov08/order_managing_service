from typing import Annotated
from fastapi import Depends

from app.services.auth import AuthService
from app.services.tokens import TokenService
from app.utils import LoggerDep
from app.common.deps import CommonPostgresDep
from app.api.tokens.controllers.deps import TokenServiceDep


def _get_auth_service(
    logger: LoggerDep,
    postgres_adapter: CommonPostgresDep,
    token_service: TokenServiceDep
) -> AuthService:
    return AuthService(
        logger=logger,
        postgres_adapter=postgres_adapter,
        token_service=token_service
    )

AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]
