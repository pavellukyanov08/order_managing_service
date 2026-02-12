import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from starlette.middleware import Middleware
import redis.asyncio as redis

from .api.users.controllers import router as user_router
from .api.auth.controllers import router as auth_router
from .api.orders.controllers import router as order_router
from .api.tokens.controllers import router as token_router
from .settings.redis import redis_settings
from .core.database import async_engine
from .utils.logger import LoggerMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application...")

    redis_client = redis.Redis(
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
    yield
    await app.state.redis_client.aclose()


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

app.add_middleware(LoggerMiddleware)


if __name__ == '__main__':
    uvicorn.run("main:proj_app", host="0.0.0.0", port=8000, reload=True)
