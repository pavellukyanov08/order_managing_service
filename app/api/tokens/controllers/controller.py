from typing import Annotated

from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm, HTTPBearer

from app.settings import api_settings
from .deps import TokenServiceDep
from app.schemas import (
    TokenPair,
    RefreshToken,
    CreateTokenPair,
)


router = APIRouter(
    prefix=api_settings.TOKENS_PREFIX,
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)


@router.post('/create', response_model=TokenPair)
async def create_tokens(
    service: TokenServiceDep,
    data: Annotated[CreateTokenPair, Body(...)]
) -> TokenPair:

    return await service.create_token_pair(data=data)


@router.post('/refresh', response_model=TokenPair)
async def refresh_token(
    service: TokenServiceDep,
    data: Annotated[RefreshToken, Body(...)]
) -> TokenPair:

    return await service.refresh_token_pair(data=data)
