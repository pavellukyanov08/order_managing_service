from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from app.enums import OrderStatus


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


class OrderRead(OrderBase):
    id: int = Field(...)
    user_sid: UUID = Field(..., description="SID of user")
    created_at: datetime = Field(..., description="Wallet created at")
    updated_at: datetime = Field(..., description="Wallet updated at")


