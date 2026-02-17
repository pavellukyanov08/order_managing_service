from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Path, Depends
from fastapi.security import HTTPBearer

from app.schemas.user import UserCreate
from app.settings import api_settings
from .deps import UserServiceDep
from app.deps import CurrentActiveUserDep
from app.common.schemas import UserDTO, MessageDTO


router = APIRouter(
    prefix=api_settings.USERS_PREFIX,
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)


@router.get('/get_me', response_model=UserDTO)
async def get_me(
    service: UserServiceDep,
    current_user: CurrentActiveUserDep
) -> UserDTO:
    return await service.get_me(current_user=current_user)


@router.post(
    '/create_user',
    response_model=UserDTO
)
async def create_user(
    service: UserServiceDep,
    user_data: Annotated[UserCreate, Body(...)],
) -> UserDTO:
    return await service.create_user(data=user_data)


@router.patch('/block_user/{userSid}', response_model=MessageDTO)
async def block_user(
    service: UserServiceDep,
    current_user: CurrentActiveUserDep,
    user_sid: Annotated[UUID, Path(..., alias="userSid")]
) -> MessageDTO:
    await service.block_user(current_user=current_user, user_sid=user_sid)

    return MessageDTO(message="Учетная запись пользователя отключена")


@router.patch('/unlock_user/{userSid}', response_model=MessageDTO)
async def unlock_user(
    service: UserServiceDep,
    current_user: CurrentActiveUserDep,
    user_sid: Annotated[UUID, Path(..., alias="userSid")]
) -> MessageDTO:
    await service.unlock_user(current_user=current_user, user_sid=user_sid)

    return MessageDTO(message="Учетная запись пользователя активирована")


