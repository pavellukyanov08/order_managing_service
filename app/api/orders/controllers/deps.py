from typing import Annotated
from fastapi import Depends
from app.services.orders import OrderService
from app.common.deps import CommonPostgresDep, CommonRedisDep, CommonRabbitMQDep


def _get_order_service(
    postgres_adapter: CommonPostgresDep,
    redis_adapter: CommonRedisDep,
    rabbitmq_adapter: CommonRabbitMQDep,
) -> OrderService:
    return OrderService(
        postgres_adapter=postgres_adapter,
        redis_adapter=redis_adapter,
        rabbitmq_adapter=rabbitmq_adapter,
    )


OrderServiceDep = Annotated[OrderService, Depends(_get_order_service)]
