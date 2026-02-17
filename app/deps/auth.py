from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from starlette import status

from app.common.schemas import UserDTO
from app.core.auth import jwt_auth
from app.common.deps import CommonPostgresDep
from .validation import validate_token_type
from app.enums import TokenTypeEnum, UserStatusEnum


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_token_payload(
    token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = jwt_auth.decode_token(token=token)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token error: {e}",
        )
    return payload


async def get_current_active_user(
    postgres: CommonPostgresDep,
    payload: dict[str, Any] = Depends(get_current_token_payload),
) -> UserDTO:
    validate_token_type(
        payload=payload,
        token_type=TokenTypeEnum.ACCESS,
    )
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
    if user.status == UserStatusEnum.BLOCKED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has been blocked",
        )
    return user


CurrentActiveUserDep = Annotated[UserDTO, Depends(get_current_active_user)]
