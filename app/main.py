import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware import Middleware
from redis.asyncio import Redis as RedisClient
import aio_pika

from app.utils.logger import init_logging
from .api.users.controllers import router as user_router
from .api.auth.controllers import router as auth_router
from .api.orders.controllers import router as order_router
from .api.tokens.controllers import router as token_router
from .settings.redis import redis_settings
from .settings.rabbitmq import rabbitmq_settings
from .utils.middleware import LoggerMiddleware


app_logger = init_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_logger.info("Starting application...")

    redis_client = RedisClient(
        host=redis_settings.HOST,
        port=redis_settings.PORT,
        username=redis_settings.USER,
        password=redis_settings.PASSWORD,
        max_connections=redis_settings.MAX_CONNECTIONS,
        socket_timeout=redis_settings.SOCKET_TIMEOUT,
        socket_connect_timeout=redis_settings.SOCKET_CONNECT_TIMEOUT,
        health_check_interval=redis_settings.HEALTHCHECK_INTERVAL,
        decode_responses=False
    )

    await redis_client.ping()
    app.state.redis_client = redis_client
    app_logger.info("Redis connected")

    rabbitmq_connection = await aio_pika.connect_robust(rabbitmq_settings.url)
    app_logger.info("RabbitMQ connected")

    from app.common.adapters import RabbitMQAdapter
    rabbitmq_adapter = RabbitMQAdapter(
        logger=app_logger,
        connection=rabbitmq_connection,
    )
    await rabbitmq_adapter.setup(
        exchange_name="orders",
        queue_name="q.order.new",
        routing_key="new_order",
        dlx_exchange_name="dlx.orders",
        dlq_queue_name="dlq.order.new",
        dlq_routing_key="dead.order.new",
    )
    app.state.rabbitmq_adapter = rabbitmq_adapter
    app.state.rabbitmq_connection = rabbitmq_connection

    yield

    await app.state.rabbitmq_adapter.close()
    await app.state.rabbitmq_connection.close()
    app_logger.info("RabbitMQ disconnected")

    await app.state.redis_client.aclose()
    app_logger.info("Shutdown complete")


app = FastAPI(
    title="Система управления заказами пользователей",
    lifespan=lifespan,
    middleware=[
        Middleware(LoggerMiddleware)
    ],
)


@app.get('/', include_in_schema=False)
def redirect_to_docs():
    return RedirectResponse(url="/docs")


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(order_router)
app.include_router(token_router)


if __name__ == '__main__':
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
