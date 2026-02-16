from faststream.rabbit import RabbitBroker, RabbitPublisher

from app.schemas.order.broker_order import CreateOrderEvent
from app.utils import LoggerDep



class RabbitMQAdapter:
    def __init__(
        self,
        *,
        logger: LoggerDep,
        rabbit_client: RabbitBroker,
    ) -> None:
        self._logger = logger
        self._rabbit_client = rabbit_client

    async def publish_new_order_event(
        self, *, data: CreateOrderEvent
    ) -> None:
        customer = str(data.customer)

        try:
            await RabbitPublisher.publish(
                rabbit_client=self._rabbit_client,
                message=data,
                exchange=SETTINGS.rabbit.SSO_EMAIL_EXCHANGE,
                routing_key=SETTINGS.rabbit.SSO_EMAIL_QUEUE_ROUTING_KEY,
                expired_at=DateTimeManager.get_now_utc()
                + timedelta(seconds=SETTINGS.auth.TWO_FACTOR_CODE_TTL),
                request_id=self._request_id,
                request_id_header=self._request_id_header,
            )

            self._logger.info(
                "Email for 2FA successfully sent "
                "(Subject: %s, Sender: %s, Recipients: %s)",
                data.subject,
                masked_sender,
                masked_recipients,
            )
        except Exception as e:
            self._logger.error(
                "Failed to sent email for 2FA "
                "(Subject: %s, Sender: %s, Recipients: %s) error: %s",
                data.subject,
                masked_sender,
                masked_recipients,
                e,
            )
            raise