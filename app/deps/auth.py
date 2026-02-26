from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette import status

from app.common.schemas import UserDTO
from app.common.deps import CommonPostgresDep
from app.api.tokens.controllers.deps import TokenServiceDep
from app.enums import TokenTypeEnum, UserStatusEnum


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


async def get_current_active_user(
    postgres: CommonPostgresDep,
    token_service: TokenServiceDep,
    token: str = Depends(oauth2_scheme),
) -> UserDTO:
    token_model = await token_service.check_token(
        token=token,
        token_type=TokenTypeEnum.ACCESS,
    )

    user = await postgres.get_user(user_sid=token_model.token_sub)
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
