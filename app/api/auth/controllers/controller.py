from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.common.schemas import MessageDTO
from app.schemas import AuthLoginResult, TokenPair, AuthLogin
from app.settings import api_settings
from app.deps import CurrentActiveUserDep
from .deps import AuthServiceDep



http_bearer = HTTPBearer(auto_error=False)

router = APIRouter(
    prefix=api_settings.AUTH_USERS_PREFIX,
    dependencies=[Depends(http_bearer)],
)


@router.post('/login', response_model=AuthLoginResult)
async def login(
    service: AuthServiceDep,
    data: AuthLogin,
) -> AuthLoginResult:

    return await service.login(user_data=data)


@router.post('/login_swagger', response_model=TokenPair)
async def login_swagger(
    service: AuthServiceDep,
    data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> TokenPair:
    auth_data = AuthLogin(
        email=data.username,
        password=data.password
    )

    return await service.login(user_data=auth_data)


@router.post('/logout', response_model=MessageDTO)
async def logout(
    service: AuthServiceDep,
    current_user: CurrentActiveUserDep
) -> MessageDTO:
    await service.logout(user_data=current_user)

    return MessageDTO(message="Успешный выход из системы")