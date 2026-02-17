import time

from app.core.celery import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id: int):
    try:
        time.sleep(2)
        print(f"Order {order_id} processed")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)
