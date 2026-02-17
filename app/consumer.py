import asyncio
import json
import logging

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.settings import rabbitmq_settings
from app.api.orders.tasks.order import process_order


logger = logging.getLogger("consumer")
logging.basicConfig(level=logging.INFO)

MAX_RETRIES = 3


async def on_new_order(message: AbstractIncomingMessage) -> None:
    try:
        body = json.loads(message.body.decode())
        order_id = body.get("order_id")
        if not order_id:
            logger.error("No order_id in message, sending to DLQ")
            await message.nack(requeue=False)
            return

        death_count = 0
        if message.headers and "x-death" in message.headers:
            death_count = message.headers["x-death"][0].get("count", 0)

        if death_count >= MAX_RETRIES:
            logger.error(
                "order_id=%s exceeded max retries (%s), dropping",
                order_id,
                MAX_RETRIES,
            )
            await message.nack(requeue=False)
            return

        logger.info("Received new_order event: order_id=%s (retry=%s)", order_id, death_count)

        process_order.delay(order_id=order_id)
        logger.info("Dispatched Celery task for order_id=%s", order_id)
        await message.ack()

    except Exception as e:
        logger.error("Failed to process message: %s, sending to DLQ", e)
        await message.nack(requeue=False)


async def main() -> None:
    logger.info("Starting RabbitMQ consumer...")
    connection = await aio_pika.connect_robust(rabbitmq_settings.url)

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        exchange = await channel.declare_exchange(
            "orders",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        dlx = await channel.declare_exchange(
            "dlx.orders",
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )

        dlq = await channel.declare_queue(
            "dlq.order.new",
            durable=True,
            arguments={
                "x-message-ttl": 30000,
                "x-dead-letter-exchange": "orders",
                "x-dead-letter-routing-key": "new_order",
            },
        )
        await dlq.bind(dlx, routing_key="dead.order.new")

        queue = await channel.declare_queue(
            "q.order.new",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx.orders",
                "x-dead-letter-routing-key": "dead.order.new",
            },
        )
        await queue.bind(exchange, routing_key="new_order")

        await queue.consume(on_new_order)
        logger.info("Consuming from queue=q.order.new (DLX enabled, max_retries=%s)", MAX_RETRIES)

        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
