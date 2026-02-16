import logging
import logging.config
from fastapi import Request
from typing import Annotated
from fastapi import Depends
import os
from pathlib import Path

from app.core.logger import LOGGING_CONFIG


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
os.chmod(LOG_DIR, 0o755)


def init_logging() -> logging.Logger:
    logging.config.dictConfig(LOGGING_CONFIG)

    logger = logging.getLogger("app_logger")
    logger.info("🚀 Logging initialized - logs/app.log ready")

    return logger


def _get_logger(request: Request) -> logging.Logger:
    logger: logging.Logger | None = getattr(request.state, "logger", None)
    if not logger:
        raise RuntimeError("Missing required request state: logger")
    return logger


LoggerDep = Annotated[logging.Logger, Depends(_get_logger)]