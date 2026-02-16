from typing import Annotated
from fastapi import Depends

from app.services.auth import AuthService
from app.common.deps import CommonPostgresDep
from app.api.tokens.controllers.deps import TokenServiceDep


def _get_auth_service(
    postgres_adapter: CommonPostgresDep,
    token_service: TokenServiceDep
) -> AuthService:
    return AuthService(
        postgres_adapter=postgres_adapter,
        token_service=token_service
    )

AuthServiceDep = Annotated[AuthService, Depends(_get_auth_service)]
