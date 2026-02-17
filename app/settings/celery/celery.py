from pydantic import Field
from pydantic_settings import BaseSettings


class CelerySettings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    BROKER_URL: str = Field(..., alias="CELERY_BROKER_URL")
    RESULT_BACKEND: str = Field(..., alias="CELERY_RESULT_BACKEND")


celery_settings = CelerySettings()
