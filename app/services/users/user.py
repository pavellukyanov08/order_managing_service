import logging
from uuid import uuid4, UUID

from fastapi import HTTPException

from app.deps import CurrentActiveUserDep, check_user_admin
from app.utils import DateTimeManager
from app.common.adapters import PostgresAdapter
from app.common.schemas import UserDTO, MessageDTO
from app.core.auth import password_manager
from app.schemas.user import UserCreate


class UserService:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        postgres_adapter: PostgresAdapter,
    ) -> None:
        self._logger = logger
        self._postgres_adapter = postgres_adapter

    async def commit_user(self) -> None:
        await self._postgres_adapter.commit()

    @staticmethod
    def _get_user_model(
        *,
        user_data: UserCreate,
    ) -> UserDTO:
        hashed_password = password_manager.get_hashed_password(
            password=user_data.password,
        )
        created_at = DateTimeManager.get_now_utc()
        fullname = ' '.join(filter(None, [user_data.first_name, user_data.last_name, user_data.middle_name]))
        return UserDTO(
            sid=uuid4(),
            email=user_data.email,
            fullname=fullname,
            hashed_password=hashed_password,
            created_at=created_at,
            updated_at=created_at
        )

    @staticmethod
    async def get_me(
        *,
        current_user: CurrentActiveUserDep
    ) -> UserDTO:
        return UserDTO.model_validate(current_user)

    async def get_user(
        self,
        *,
        user_sid: UUID,
    ) -> UserDTO:
        user = await self._postgres_adapter.get_user(user_sid=user_sid)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist",
            )
        return UserDTO.model_validate(user)

    async def create_user(
        self,
        *,
        data: UserCreate,
    ) -> UserDTO:
         user_by_email = await self._postgres_adapter.get_user_by_email(
             user_email=data.email,
         )
         if user_by_email:
             raise HTTPException(
                 status_code=400,
                 detail="User with this email already exists",
             )

         if data.password != data.confirm_password:
             raise HTTPException(
                 status_code=400,
                 detail="Passwords do not match",
             )

         user_model = self._get_user_model(user_data=data)
         await self._postgres_adapter.create_user(user_model=user_model)
         await self.commit_user()
         return user_model

    async def block_user(
        self,
        user_sid: UUID,
        current_user: CurrentActiveUserDep
    ) -> MessageDTO:
        user = await self._postgres_adapter.get_user(user_sid=user_sid)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist",
            )
        await check_user_admin(user_sid=current_user.sid, postgres=self._postgres_adapter)
        await self._postgres_adapter.block_user(user_sid=user_sid)
        await self._postgres_adapter.commit()
        return MessageDTO(message="Учетная запись успешно отключена")

    async def unlock_user(
        self,
        *,
        user_sid: UUID,
        current_user: CurrentActiveUserDep,
    ) -> MessageDTO:
        user = await self._postgres_adapter.get_user(user_sid=user_sid)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail="User does not exist",
            )
        await check_user_admin(user_sid=current_user.sid, postgres=self._postgres_adapter)
        await self._postgres_adapter.unlock_user(user_sid=user_sid)
        await self._postgres_adapter.commit()
        return MessageDTO(message="Учетная запись успешно активирована")


