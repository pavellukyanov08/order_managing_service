from fastapi import HTTPException
from starlette import status

from app.common.deps import CommonPostgresDep
from app.common.schemas import UserDTO
from app.core.auth import password_manager
from app.enums import TokenTypeEnum
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
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User inactive",
        )
    if user.hashed_password is None or not password_manager.verify_password(
            user_password=user_data.password, hashed_password=user.hashed_password
    ):
        raise unauth_error
    return user


def validate_token_type(
    payload: dict,
    token_type: TokenTypeEnum,
) -> bool:
    if payload.get("token_type") == token_type:
        return True
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token type {payload.get('token_type')} expected {token_type}",
    )