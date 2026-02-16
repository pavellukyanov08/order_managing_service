from datetime import datetime
from typing import Any, Self
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator
from app.enums import OrderStatus
from app.utils import NormalizeDateTime


class OrderBase(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    total_price: float = Field(...)
    status: OrderStatus = Field(...)

    @field_validator('items', mode='before')
    def fix_items(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v


class OrderCreate(OrderBase):
    user_sid: UUID = Field(...)
    created_at: datetime = Field(...)


class OrderUpdate(BaseModel):
    id: int = Field(...)
    status: OrderStatus = Field(...)
    updated_at: datetime = Field(...)


class OrderRead(OrderBase, NormalizeDateTime):
    id: int = Field(...)
    user_sid: UUID = Field(..., description="SID of user")
    created_at: datetime = Field(..., description="Wallet created at")
    updated_at: datetime = Field(..., description="Wallet updated at")

    redis_key: str = Field(
        "", exclude=True, description="Order key for redis"
    )

    @staticmethod
    def build_redis_key(
        *,
        idx: int | None = None,
        items: list[dict[str, Any]] | None = None,
        total_price: float | None = None,
        status: OrderStatus | None = None,
    ) -> str:
        return (
            f"order:{idx or '*'}:"
            f"{items or '*'}:"
            f"{total_price or '*'}"
            f"{status or '*'}"
        )

    @model_validator(mode="after")
    def create_redis_key(self) -> Self:
        self.redis_key = self.build_redis_key(
            idx=self.id,
            items=self.items,
            total_price=self.total_price,
            status=self.status,
        )
        return self


