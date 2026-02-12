from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Annotated
from fastapi import Request, Depends


class LoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = logging.getLogger("app_logger")
        request.state.logger = logger
        response = await call_next(request)
        return response


def _get_logger(request: Request) -> logging.Logger:
    logger: logging.Logger | None = getattr(request.state, "logger", None)
    if not logger:
        raise RuntimeError("Missing required request state: logger")
    return logger


LoggerDep = Annotated[logging.Logger, Depends(_get_logger)]