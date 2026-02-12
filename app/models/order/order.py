from datetime import datetime
from uuid import UUID

from pydantic import Field
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import OrderStatus
from app.utils import DateTimeManager


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    items: Mapped[list[dict]] = mapped_column(JSONB, comment="Товары в заказе")
    total_price: Mapped[float] = mapped_column()
    status: Mapped[OrderStatus] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc,
        onupdate=DateTimeManager.get_now_utc,
    )
    user_sid: Mapped[UUID] = mapped_column(
        ForeignKey("user.sid", ondelete="CASCADE"),
    )

    user = relationship(
        "User",
        foreign_keys=[user_sid],
        back_populates="orders",
    )

    redis_key: str = Field(
        "", exclude=True, description="Order key for redis"
    )

    @staticmethod
    def build_redis_key(
        *,
        idx: int | None = None,
        items: JSONB | None = None,
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
            sid=self.sid,
            token_sub=self.token_sub,
            token_type=self.token_type,
        )
        return self
