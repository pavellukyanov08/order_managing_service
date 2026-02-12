from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from starlette import status

from app.common.schemas import UserDTO
from app.core.auth import jwt_auth
from app.common.deps import CommonPostgresDep
from .validation import validate_token_type
from app.enums import TokenTypeEnum


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login_swagger"
)


async def get_user_by_token_sub(
    payload: dict,
    postgres: CommonPostgresDep,
) -> UserDTO:
    user_sid = payload.get('token_sub')
    if not user_sid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    user = await postgres.get_user(user_sid=user_sid)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = jwt_auth.decode_token(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


async def get_current_user(
    *,
    payload: dict = Depends(get_current_token_payload),
    postgres: CommonPostgresDep
) -> UserDTO:
    validate_token_type(
        payload=payload,
        token_type=TokenTypeEnum.ACCESS,
    )
    return await get_user_by_token_sub(payload=payload, postgres=postgres)


async def get_current_user_for_refresh(
    *,
    payload: dict = Depends(get_current_token_payload),
    postgres: CommonPostgresDep
) -> UserDTO:
    validate_token_type(
        payload=payload,
        token_type=TokenTypeEnum.REFRESH,
    )
    return await get_user_by_token_sub(payload=payload, postgres=postgres)


def get_current_active_user(
    user: UserDTO = Depends(get_current_user),
) -> UserDTO:
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return user


CurrentActiveUserDep = Annotated[UserDTO, Depends(get_current_active_user)]
CurrentUserRefreshDep = Annotated[UserDTO, Depends(get_current_user_for_refresh)]