import json
import aio_pika
from aio_pika import Message, DeliveryMode
from aio_pika.abc import AbstractRobustConnection, AbstractRobustChannel, AbstractRobustExchange

from app.utils import LoggerDep


class RabbitMQAdapter:
    def __init__(
        self,
        *,
        logger: LoggerDep,
        connection: AbstractRobustConnection,
    ) -> None:
        self._logger = logger
        self._connection = connection
        self._channel: AbstractRobustChannel | None = None
        self._exchanges: dict[str, AbstractRobustExchange] = {}

    async def setup(
        self,
        *,
        exchange_name: str,
        queue_name: str,
        routing_key: str,
        dlx_exchange_name: str | None = None,
        dlq_queue_name: str | None = None,
        dlq_routing_key: str | None = None,
        dlq_ttl: int = 30000,
    ) -> None:
        self._channel = await self._connection.channel()

        exchange = await self._channel.declare_exchange(
            exchange_name,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        self._exchanges[exchange_name] = exchange

        queue_arguments: dict = {}

        if dlx_exchange_name:
            dlx = await self._channel.declare_exchange(
                dlx_exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            self._exchanges[dlx_exchange_name] = dlx

            _dlq_queue_name = dlq_queue_name or f"{queue_name}_dlq"
            _dlq_routing_key = dlq_routing_key or routing_key

            dlq = await self._channel.declare_queue(
                _dlq_queue_name,
                durable=True,
                arguments={
                    "x-message-ttl": dlq_ttl,
                    "x-dead-letter-exchange": exchange_name,
                    "x-dead-letter-routing-key": _dlq_routing_key,
                },
            )
            await dlq.bind(dlx, routing_key=_dlq_routing_key)

            queue_arguments["x-dead-letter-exchange"] = dlx_exchange_name
            queue_arguments["x-dead-letter-routing-key"] = _dlq_routing_key

        queue = await self._channel.declare_queue(
            queue_name,
            durable=True,
            arguments=queue_arguments or None,
        )
        await queue.bind(exchange, routing_key=routing_key)

        self._logger.info(
            "RabbitMQ setup complete: exchange=%s queue=%s routing_key=%s",
            exchange_name,
            queue_name,
            routing_key,
        )

    async def publish(
        self,
        *,
        exchange_name: str,
        routing_key: str,
        body: dict,
    ) -> None:
        exchange = self._exchanges.get(exchange_name)
        if not exchange:
            raise RuntimeError(
                f"Exchange '{exchange_name}' not set up. Call setup() first."
            )

        message = Message(
            body=json.dumps(body).encode(),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
        )
        await exchange.publish(message, routing_key=routing_key)
        self._logger.info(
            "Published message to exchange=%s routing_key=%s",
            exchange_name,
            routing_key,
        )

    async def close(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
