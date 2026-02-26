from pydantic import Field
from pydantic_settings import BaseSettings


class RabbitMQSettings(BaseSettings):
    model_config = {"env_file": ".env", "extra": "ignore"}

    HOST: str = Field(..., alias="RABBITMQ_HOST")
    PORT: int = Field(..., alias="RABBITMQ_PORT")
    USER: str = Field(..., alias="RABBITMQ_USER")
    PASSWORD: str = Field(..., alias="RABBITMQ_PASSWORD")
    VHOST: str = Field("/", alias="RABBITMQ_VHOST")

    @property
    def url(self) -> str:
        from urllib.parse import quote
        vhost = quote(self.VHOST, safe="")
        return f"amqp://{self.USER}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{vhost}"


rabbitmq_settings = RabbitMQSettings()
