from uuid import UUID

from fastapi import HTTPException
from starlette import status

from app.common.deps import CommonPostgresDep
from app.common.schemas import UserDTO
from app.enums import UserStatusEnum, UserRoleEnum
from app.core.auth import password_manager
from app.schemas import AuthLogin


async def validate_auth_user(
    *,
    user_data: AuthLogin,
    postgres: CommonPostgresDep
) -> UserDTO:
    unauth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
    )
    user = await postgres.get_user_by_email(
        user_email=user_data.email,
    )
    if user is None:
        raise unauth_error
    if user.status == UserStatusEnum.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has been blocked",
        )
    if user.hashed_password is None or not password_manager.verify_password(
            user_password=user_data.password, hashed_password=user.hashed_password
    ):
        raise unauth_error
    return user


async def check_user_admin(
    *,
    user_sid: UUID,
    postgres: CommonPostgresDep
) -> None:
    unauth_error = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User does not exist",
    )
    user = await postgres.get_user(user_sid=user_sid)
    if user is None:
        raise unauth_error
    if user.role != UserRoleEnum.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )