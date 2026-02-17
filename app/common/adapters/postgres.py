from typing import cast
from uuid import UUID

from pydantic import EmailStr
from sqlalchemy import ColumnElement, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import UserStatusEnum
from app.utils import LoggerDep
from app.models import User, Order
from app.common.schemas import UserDTO
from app.schemas import (
    OrderRead,
    OrderUpdate,
    OrderCreate,
)
from app.utils import DateTimeManager


class PostgresAdapter:
    def __init__(
        self,
        *,
        logger: LoggerDep,
        postgres_session: AsyncSession,

    ) -> None:
        self._logger = logger
        self._postgres_session = postgres_session

    async def commit(self) -> None:
        try:
            await self._postgres_session.commit()
            self._logger.info("Changes has been commited")
        except Exception as e:
            self._logger.error("Error while commiting changes: %s", e)
            await self.rollback()
            raise

    async def rollback(self) -> None:
        try:
            await self._postgres_session.rollback()
            self._logger.info("Changes has been cancelled")
        except Exception as e:
            self._logger.error("Error when cancelling changes: %s", e)
            raise

    @staticmethod
    def _create_user_model(
        *,
        user_alchemy_model: User,
    ) -> UserDTO:
        return UserDTO(
            sid=user_alchemy_model.sid,
            email=cast(EmailStr, user_alchemy_model.email),
            fullname=user_alchemy_model.fullname,
            hashed_password=user_alchemy_model.hashed_password,
            created_at=user_alchemy_model.created_at,
            updated_at=user_alchemy_model.created_at,
        )

    async def _get_user_model(
        self,
        *,
        user_result: ColumnElement[bool]
    ) -> UserDTO | None:
        query = (
            select(User)
            .where(user_result)
        )
        stmt = await self._postgres_session.execute(query)
        result = stmt.scalar_one_or_none()

        if result is None:
            return None

        user_dto_model = UserDTO.model_validate(
            obj=result, from_attributes=True
        )
        return user_dto_model

    async def get_user(
        self,
        *,
        user_sid: UUID
    ) -> User | None:
        try:
            user_model = await self._get_user_model(
                user_result=(User.sid == user_sid),
            )

            self._logger.info(
                "Received user user_sid=%s",
                user_sid,
            )
            return user_model
        except Exception as e:
            self._logger.info(
                "Failed receiving user: user_sid=%s error=%s",
                user_sid,
                e,
            )
            raise

    async def get_user_by_email(
        self, *, user_email: EmailStr
    ) -> User | None:
        try:
            user_model = await self._get_user_model(
                user_result=(
                    User.email == user_email
                ),
            )
            self._logger.info(
                "Received user by user_email=%s",
                user_email,
            )
            return user_model
        except Exception as e:
            self._logger.info(
                "Failed to receive user: user_email=%s error=%s",
                user_email,
                e,
            )
            raise

    async def get_order(
        self,
        *,
        order_id: int
    ) -> Order | None:
        try:
            stmt = select(Order).where(Order.id == order_id)
            result = await self._postgres_session.execute(stmt)
            order: Order = result.scalar_one_or_none()
            self._logger.info(
                "Received order order_id=%s",
                order_id,
            )
            return order
        except Exception as e:
            self._logger.info(
                "Failed receiving order: order_id=%s error=%s",
                order_id,
                e,
            )
            raise

    async def get_orders_by_user(
        self,
        *,
        user_sid: UUID
    ) -> list[Order]:
        try:
            stmt = select(Order).where(Order.user_sid == user_sid)
            result = await self._postgres_session.execute(stmt)
            orders = result.scalars().all()
            self._logger.info(
                "Received order by user_sid=%s",
                user_sid,
            )
            return orders
        except Exception as e:
            self._logger.info(
                "Failed receiving order by user_sid: user_sid=%s error=%s",
                user_sid,
                e,
            )
            raise
        
    async def create_order(self, *, order_data: OrderCreate) -> Order:
        try:
            updated_at = DateTimeManager.get_now_utc()
            order = Order(
                items=order_data.items,
                total_price=order_data.total_price,
                status=order_data.status,
                user_sid=order_data.user_sid,
                created_at=order_data.created_at,
                updated_at=updated_at,
            )
            self._postgres_session.add(order)
            self._logger.info("Order has been created: %s", order_data.items)
            await self._postgres_session.flush()
            return order
        except Exception as e:
            self._logger.error(
                "Failed while creating order: item=%s error=%s",
                order_data.items,
                e,
            )
            await self.rollback()
            raise

    async def update_order(
        self,
        *,
        updated_order: OrderUpdate,
    ) -> None:
        try:
            order = await self._postgres_session.execute(
                update(Order)
                .where(Order.id == updated_order.id)
                .values(
                    status=updated_order.status,
                    updated_at=updated_order.updated_at,
                )
            )
            self._logger.info("Order has been updated: %s",
                            updated_order.id
            )
        except SQLAlchemyError as e:
            self._logger.info("Error while updating Order: %s", e)
            await self.rollback()
            raise

    async def check_user_exists(
        self,
        *,
        user_sid: UUID
    ) -> bool:
        query = select(User.sid).where(User.sid == user_sid)
        stmt = await self._postgres_session.execute(query)
        result = stmt.first()
        if result is None:
            return False
        return True

    async def create_user(self, *, user_model: UserDTO) -> None:
        try:
            if not await self.check_user_exists(user_sid=user_model.sid):
                user = User(
                    sid=user_model.sid,
                    fullname=user_model.fullname,
                    email=str(user_model.email),
                    hashed_password=user_model.hashed_password,
                    created_at=user_model.created_at,
                    updated_at=user_model.created_at,
                )
                self._postgres_session.add(user)
                self._logger.info("User has been created: %s", user_model.sid)
        except Exception as e:
            self._logger.error(
                "Failed creating user: sid=%s error=%s",
                user_model.sid,
                e,
            )
            await self.rollback()
            raise

    async def block_user(
        self,
        *,
        user_sid: UUID
    ) -> None:
        try:
            await self._postgres_session.execute(
                update(User)
                .where(User.sid == user_sid)
                .values(
                    status=UserStatusEnum.BLOCKED,
                    updated_at=DateTimeManager.get_now_utc(),
                )
            )
            self._logger.info(
                "Blocked user: sid=%s",
                user_sid,
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Failed to block user:sid=%s error=%s",
                user_sid,
                e,
            )
            await self.rollback()
            raise

    async def unlock_user(
        self,
        *,
        user_sid: UUID
    ) -> None:
        try:
            await self._postgres_session.execute(
                update(User)
                .where(User.sid == user_sid)
                .values(
                    status=UserStatusEnum.ACTIVE,
                    updated_at=DateTimeManager.get_now_utc(),
                )
            )
            self._logger.info(
                "Unlocked user: sid=%s",
                user_sid,
            )
        except SQLAlchemyError as e:
            self._logger.error(
                "Failed to unlock user:sid=%s error=%s",
                user_sid,
                e,
            )
            await self.rollback()
            raise