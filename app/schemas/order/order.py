from datetime import datetime
from typing import Self, Any
from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator, field_serializer

from app.enums import OrderStatus
from app.utils import NormalizeDateTime


class OrderBase(BaseModel):
    items: list[dict[str, Any]] = Field(default_factory=list)
    status: OrderStatus = Field()

    @field_validator('items', mode='before')
    def validate_items(cls, v):
        if v is None:
            return []
        if isinstance(v, dict):
            return [v]
        return v

    @model_validator(mode='after')
    def calculate_total_price(self) -> 'OrderBase':
        total_price = sum(
            item.get('quantity', 0) * item.get('price', 0)
            for item in self.items
        )
        object.__setattr__(self, 'total_price', round(total_price, 2))
        return self


class OrderCreate(OrderBase):
    created_at: datetime | None = Field(None, exclude=True)


class OrderUpdate(BaseModel):
    status: OrderStatus = Field(...)


class OrderRead(OrderBase, NormalizeDateTime):
    id: int = Field(...)
    total_price: float = Field(...)
    user_sid: UUID = Field(..., description="SID of user")
    created_at: datetime = Field(..., description="Order created at")
    updated_at: datetime = Field(..., description="Order updated at")

    redis_key: str = Field(
        "", exclude=True, description="Order key for redis"
    )

    @model_validator(mode="after")
    def create_redis_key(self) -> Self:
        self.redis_key = f"order:{self.id}"
        return self


