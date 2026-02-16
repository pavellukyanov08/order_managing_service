from typing import Annotated
from fastapi import Depends
from app.services.orders import OrderService
from app.common.deps import CommonPostgresDep, CommonRedisDep


def _get_order_service(
    postgres_adapter: CommonPostgresDep,
    redis_adapter: CommonRedisDep,
) -> OrderService:
    return OrderService(
        postgres_adapter=postgres_adapter,
        redis_adapter=redis_adapter,
    )


OrderServiceDep = Annotated[OrderService, Depends(_get_order_service)]
