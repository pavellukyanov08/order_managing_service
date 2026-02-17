from uuid import UUID
from fastapi import HTTPException

from app.deps import CurrentActiveUserDep
from app.common.adapters import PostgresAdapter, RedisAdapter, RabbitMQAdapter
from app.models import Order
from app.schemas import (
    OrderRead,
    OrderUpdate,
    OrderCreate
)


class OrderService:
    def __init__(
        self,
        *,
        postgres_adapter: PostgresAdapter,
        redis_adapter: RedisAdapter,
        rabbitmq_adapter: RabbitMQAdapter,
    ) -> None:
        self._postgres_adapter = postgres_adapter
        self._redis_adapter = redis_adapter
        self._rabbitmq_adapter = rabbitmq_adapter

    async def commit_wallet(self) -> None:
        await self._postgres_adapter.commit()

    @staticmethod
    def _get_order_model(
        *,
        order_data: OrderRead,
    ) -> Order:
        return Order(
            id=order_data.id,
            user_sid=order_data.user_sid,
            items=order_data.items,
            total_price=order_data.total_price,
            status=order_data.status,
            created_at=order_data.created_at,
            updated_at=order_data.updated_at,
        )

    async def get_order_by_id(
        self,
        *,
        order_id: int,
    ) -> OrderRead:
        redis_order = await self._redis_adapter.get_order(order_id=order_id)
        if redis_order:
            return redis_order

        db_order = await self._postgres_adapter.get_order(order_id=order_id)
        if db_order is None:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        order_data = OrderRead.model_validate(db_order.__dict__)

        await self._redis_adapter.set_order(order_id=order_id, order=order_data)
        return order_data

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
            update={"user_sid": current_user.sid},
        )
        order = await self._postgres_adapter.create_order(order_data=order_data)
        await self._postgres_adapter.commit()
        await self._rabbitmq_adapter.publish(
            exchange_name="orders",
            routing_key="new_order",
            body={"order_id": order.id},
        )

    async def update_order(
        self,
        *,
        data: OrderUpdate,
    ) -> None:
        order = await self._postgres_adapter.get_order(order_id=data.id)
        if order is None:
            raise HTTPException(
                status_code=404,
                detail="Order does not exist",
            )
        await self._postgres_adapter.update_order(
            updated_order=data,
        )
        updated_order = await self._postgres_adapter.get_order(order_id=data.id)
        await self._postgres_adapter.commit()
        await self._redis_adapter.set_order(
            order_id=data.id,
            order=OrderRead.model_validate(updated_order.__dict__)
        )


