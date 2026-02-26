import logging
import time

from app.core.celery import celery_app

logger = logging.getLogger("app_logger")


@celery_app.task(bind=True)
def process_order(self, order_id: int):
    try:
        time.sleep(2)
        logger.info("Order %s processed", order_id)
    except Exception as exc:
        raise self.retry(exc=exc)
