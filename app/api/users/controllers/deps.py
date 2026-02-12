from typing import Annotated
from fastapi import Depends
from app.services.users import UserService
from app.common.deps import CommonPostgresDep
from app.utils import LoggerDep


def _get_user_service(
    logger: LoggerDep,
    postgres_adapter: CommonPostgresDep,
) -> UserService:
    return UserService(
        logger=logger,
        postgres_adapter=postgres_adapter,
    )


UserServiceDep = Annotated[UserService, Depends(_get_user_service)]
