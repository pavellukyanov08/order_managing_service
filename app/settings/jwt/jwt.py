from pydantic import Field
from pydantic_settings import SettingsConfigDict, BaseSettings
from pathlib import Path


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(".env"),
        extra="ignore"
    )

    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_access_token_ttl: int = Field(..., alias="JWT_ACCESS_TOKEN_TTL")
    jwt_refresh_token_ttl: int = Field(..., alias="JWT_REFRESH_TOKEN_TTL")


jwt_settings = JWTSettings()