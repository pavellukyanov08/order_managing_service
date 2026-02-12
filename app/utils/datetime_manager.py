from datetime import datetime, timezone
from zoneinfo import ZoneInfo


class DateTimeManager:
    @staticmethod
    def get_now_utc() -> datetime:
        return datetime.now(tz=timezone.utc)

    @staticmethod
    def get_now_in_timezone(*, time_zone: str) -> datetime:
        try:
            return datetime.now(ZoneInfo(key=time_zone))
        except Exception as e:
            raise ValueError(f"Incorrect timezone: {timezone}") from e

    @staticmethod
    def convert_to_utc(*, date_time: datetime) -> datetime:
        if date_time.tzinfo is None:
            return date_time.replace(tzinfo=timezone.utc)
        return date_time.astimezone(tz=timezone.utc)
