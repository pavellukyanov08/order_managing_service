from typing import Annotated
from fastapi import Depends
from app.services.orders import OrderService
from app.common.deps import CommonPostgresDep
from app.utils import LoggerDep


def _get_order_service(
    logger: LoggerDep,
    postgres_adapter: CommonPostgresDep,
) -> OrderService:
    return OrderService(
        logger=logger,
        postgres_adapter=postgres_adapter,
    )


OrderServiceDep = Annotated[OrderService, Depends(_get_order_service)]
