from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.common.schemas import MessageDTO
from app.schemas import AuthLoginResult, AuthLogin
from app.settings import api_settings
from app.deps import CurrentActiveUserDep
from .deps import AuthServiceDep


router = APIRouter(
    prefix=api_settings.AUTH_USERS_PREFIX,
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)


@router.post('/login', response_model=AuthLoginResult)
async def login(
    service: AuthServiceDep,
    data: AuthLogin,
) -> AuthLoginResult:

    return await service.login(user_data=data)


@router.post('/logout', response_model=MessageDTO)
async def logout(
    service: AuthServiceDep,
    current_user: CurrentActiveUserDep,
) -> MessageDTO:
    await service.logout(current_user=current_user)

    return MessageDTO(message="Успешный выход из системы")