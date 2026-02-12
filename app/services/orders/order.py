import logging
from uuid import UUID
from fastapi import HTTPException

from app.deps import CurrentActiveUserDep
from app.common.adapters import PostgresAdapter, RedisAdapter
from app.schemas import (
    OrderRead,
    OrderUpdate,
    OrderCreate
)


class OrderService:
    def __init__(
        self,
        *,
        logger: logging.Logger,
        postgres_adapter: PostgresAdapter,
        redis_adapter: RedisAdapter,
    ) -> None:
        self._logger = logger
        self._postgres_adapter = postgres_adapter
        self._redis_adapter = redis_adapter

    async def commit_wallet(self) -> None:
        await self._postgres_adapter.commit()

    async def get_order_by_id(
        self,
        *,
        order_id: int,
    ) -> OrderRead:
        cache_key = f"order:{order_id}"
        cached = await self._redis_adapter.get_order()
        order = await self._postgres_adapter.get_order(order_id=order_id)
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        return OrderRead.model_validate(order)

    async def get_orders_by_user(
        self,
        *,
        user_sid: UUID,
    ) -> list[OrderRead]:
        orders = await self._postgres_adapter.get_orders_by_user(user_sid=user_sid)
        if not orders:
            raise HTTPException(status_code=404, detail="No orders found")
        return [OrderRead.model_validate(order, from_attributes=True) for order in orders]

    async def create_order(
        self,
        *,
        data: OrderCreate,
        current_user: CurrentActiveUserDep,
    ) -> None:
        order_data = data.model_copy(
            update={"user_id": current_user.sid},
        )
        await self._postgres_adapter.create_order(order_data=order_data)
        await self._postgres_adapter.commit()

    async def update_order(
        self,
        *,
        updated_order: OrderUpdate,
    ) -> None:
        order = await self.get_order_by_id(order_id=updated_order.id)
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order does not exist",
            )
        await self._postgres_adapter.update_order(
            updated_order=updated_order,
        )
        await self._postgres_adapter.commit()


