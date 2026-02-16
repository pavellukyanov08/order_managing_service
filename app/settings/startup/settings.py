from uuid import UUID

from pydantic import EmailStr, Field
from pydantic_settings import SettingsConfigDict, BaseSettings


class StartupSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    ADMIN_SID: UUID = Field(..., alias="ADMIN_SID")
    ADMIN_FIRST_NAME: str = Field(
        ..., min_length=3, max_length=64, alias="ADMIN_FIRST_NAME"
    )
    ADMIN_EMAIL: EmailStr = Field(
        ..., min_length=3, max_length=254, alias="ADMIN_EMAIL"
    )
    ADMIN_PASSWORD: str = Field(
        ..., min_length=3, max_length=99, alias="ADMIN_PASSWORD"
    )


startup_settings = StartupSettings()
