import uuid

from starlette.middleware.base import BaseHTTPMiddleware
import logging
from fastapi import Request


class LoggerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("app_logger")

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        logger = logging.LoggerAdapter(self.logger, {"request_id": request_id})

        request.state.logger = logger
        request.state.request_id = request_id

        self.logger.info("Request started", extra={"path": request.url.path})
        response = await call_next(request)

        self.logger.info(
            "Request finished",
            extra={
                "path": request.url.path,
                "status_code": response.status_code,
                "request_id": request_id
            }
        )
        return response


