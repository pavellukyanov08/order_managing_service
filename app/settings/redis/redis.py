from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}
    
    HOST: str = Field(..., alias="REDIS_HOST")
    PORT: int = Field(..., alias="REDIS_PORT")
    USER: str = Field(..., max_length=64, alias="REDIS_USER")
    PASSWORD: str = Field(..., max_length=64, alias="REDIS_PASSWORD")
    MAX_CONNECTIONS: int = Field(..., alias="REDIS_MAX_CONNECTIONS")
    SOCKET_TIMEOUT: int = Field(..., alias="REDIS_SOCKET_TIMEOUT")
    SOCKET_CONNECT_TIMEOUT: int = Field(..., alias="REDIS_SOCKET_CONNECT_TIMEOUT")
    HEALTHCHECK_INTERVAL: int = Field(..., alias="REDIS_HEALTHCHECK_INTERVAL")


redis_settings = RedisSettings()