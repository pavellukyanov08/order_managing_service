from celery import Celery
from celery.result import AsyncResult

from app.utils import LoggerDep


class CeleryAdapter:
    def __init__(self, *, logger: LoggerDep, celery_app: Celery) -> None:
        self._logger = logger
        self._celery_app = celery_app

    def send_task(
        self,
        *,
        task_name: str,
        args: tuple = (),
        kwargs: dict | None = None,
        queue: str | None = None,
    ) -> AsyncResult:
        try:
            result = self._celery_app.send_task(
                task_name,
                args=args,
                kwargs=kwargs or {},
                queue=queue,
            )
            self._logger.info(
                "Sent task=%s task_id=%s queue=%s",
                task_name,
                result.id,
                queue,
            )
            return result
        except Exception as e:
            self._logger.error(
                "Failed to send task=%s error=%s",
                task_name,
                e,
            )
            raise

    def get_task_result(self, *, task_id: str) -> AsyncResult:
        return AsyncResult(task_id, app=self._celery_app)
