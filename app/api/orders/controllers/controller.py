from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Path, Body, Depends
from fastapi.security import HTTPBearer

from app.settings import api_settings
from .deps import OrderServiceDep
from app.deps import CurrentActiveUserDep
from app.schemas import (
    OrderRead,
    OrderCreate,
    OrderUpdate,
)
from app.common.schemas import MessageDTO


router = APIRouter(
    prefix=api_settings.ORDERS_PREFIX,
    dependencies=[Depends(HTTPBearer(auto_error=False))]
)


@router.get('/{orderId}', response_model=OrderRead)
async def get_order(
    service: OrderServiceDep,
    order_id: Annotated[int, Path(..., alias="orderId")]
) -> OrderRead:
    """
    Get order by ID
    """
    return await service.get_order_by_id(order_id=order_id)


@router.get('/user/{userSid}', response_model=list[OrderRead])
async def get_orders_by_user(
    service: OrderServiceDep,
    user_sid: Annotated[UUID, Path(..., alias="userSid")]
) -> list[OrderRead]:
    """
    Get orders by user
    """
    return await service.get_orders_by_user(user_sid=user_sid)


@router.post('/create_order', response_model=MessageDTO)
async def create_order(
    service: OrderServiceDep,
    current_user: CurrentActiveUserDep,
    order_data: OrderCreate,
) -> MessageDTO:
    """
    Create an order
    """
    await service.create_order(current_user=current_user, data=order_data)
    return MessageDTO(message='Заказ создан')


@router.patch('/{order_id}/', response_model=MessageDTO)
async def update_order(
    service: OrderServiceDep,
    updated_order: Annotated[OrderUpdate, Body(...)],
) -> MessageDTO:
    """
    Update the order
    """

    await service.update_order(data=updated_order)
    return MessageDTO(message="Заказ обновлен")





