from logging import Logger

from app.common.adapters import PostgresAdapter
from app.common.schemas import UserDTO
from app.core.auth import password_manager
from app.settings.startup import startup_settings
from app.utils import DateTimeManager


class AdminStartup:
    def __init__(
        self,
        *,
        logger: Logger,
        postgres_adapter: PostgresAdapter,
    ) -> None:
        self._logger = logger
        self._postgres_adapter = postgres_adapter

    @staticmethod
    def _get_admin_model() -> UserDTO:
        created_at = DateTimeManager.get_now_utc()
        hashed_password = password_manager.get_hashed_password(
            password=startup_settings.ADMIN_PASSWORD
        )
        return UserDTO(
            sid=startup_settings.ADMIN_SID,
            fullname=startup_settings.ADMIN_FIRST_NAME,
            email=startup_settings.ADMIN_EMAIL,
            hashed_password=hashed_password,
            created_at=created_at,
            updated_at=created_at,
        )

    async def create_admin(
        self
    ) -> None:
        admin = await self._postgres_adapter.get_user(
            user_sid=startup_settings.ADMIN_SID
        )
        if admin:
            self._logger.warning(
                "Admin %s already exists",
                startup_settings.ADMIN_EMAIL,
            )
            return

        admin_model = self._get_admin_model()
        await self._postgres_adapter.create_user(
            user_model=admin_model
        )
        await self._postgres_adapter.commit()

        self._logger.info(
            "Admin %s has been successfully created %s",
            startup_settings.ADMIN_EMAIL,
        )
