from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, field_validator


class NormalizeDateTime(BaseModel):
    @field_validator("*", mode="before")
    def normalize_datetime(cls, v: Any) -> Any:
        if isinstance(v, datetime):
            if v.tzinfo is None:
                return v.replace(tzinfo=timezone.utc)
            return v.astimezone(tz=timezone.utc)
        return v
