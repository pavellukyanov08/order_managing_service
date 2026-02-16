from app.common.adapters import PostgresAdapter
from app.common.schemas import MessageDTO
from app.deps import (
    validate_auth_user,
    CurrentActiveUserDep
)
from app.schemas import CreateTokenPair, AuthLoginResult, AuthLogin
from app.services.tokens import TokenService


class AuthService:
    def __init__(
        self,
        *,
        postgres_adapter: PostgresAdapter,
        token_service: TokenService,
    ) -> None:
        self._postgres_adapter = postgres_adapter
        self._token_service = token_service

    async def login(
        self,
        *,
        user_data: AuthLogin
    ) -> AuthLoginResult:
        user = await validate_auth_user(
            user_data=user_data,
            postgres=self._postgres_adapter
        )
        get_tokens_pair = await self._token_service.create_token_pair(
            data=CreateTokenPair(
                sub=user.sid
            )
        )
        return AuthLoginResult(
            tokens=get_tokens_pair
        )

    async def logout(
        self, *, current_user: CurrentActiveUserDep
    ) -> MessageDTO:
        user = await self._postgres_adapter.get_user(user_sid=current_user.sid)
        if user is None:
            raise ValueError("Пользователя не существует")

        await self._token_service.revoke_token_pair(
            token_sub=user.sid
        )

        return MessageDTO(message="OK")
