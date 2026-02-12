import asyncio
import logging
from logging import Logger

from app.common.adapters import PostgresAdapter
from app.core.database import AsyncSessionLocal
from app.startup import AdminStartup


async def _create_admin(
    *,
    logger: Logger,
) -> None:
    async with AsyncSessionLocal() as session:
        try:
            postgres_adapter = PostgresAdapter(
                logger=logger,
                postgres_session=session,
            )
            admin_startup = AdminStartup(
                logger=logger, postgres_adapter=postgres_adapter
            )
            await admin_startup.create_admin()
            logger.info("Superuser initialized")
        except Exception as e:
            logger.error("Admin initialization error: %s", e)
            raise


async def start() -> None:
    startup_logger = logging.getLogger("app_logger")
    await _create_admin(logger=startup_logger)


if __name__ == "__main__":
    asyncio.run(start())
