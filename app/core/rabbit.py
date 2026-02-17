import aio_pika

from app.settings import rabbitmq_settings


async def create_connection():
    return await aio_pika.connect_robust(
        rabbitmq_settings.url,
    )
