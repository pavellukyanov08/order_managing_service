from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import OrderStatus
from app.utils import DateTimeManager


# order_product = Table('order_product', Base.metadata,
#     Column('product_id', Integer, ForeignKey('product.id'), primary_key=True),
#     Column('order_id', Integer, ForeignKey('order.id'), primary_key=True)
# )


class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    items: Mapped[list[dict]] = mapped_column(JSONB, nullable=True)
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
    # products: Mapped[list["Product"]] = relationship(
    #     "Product",
    #     back_populates="orders",
    #     secondary=order_product,
    # )



# class Product(Base):
#     __tablename__ = "product"
#
#     id: Mapped[int] = mapped_column(primary_key=True, index=True)
#     name: Mapped[str] = mapped_column()
#     price: Mapped[float] = mapped_column()
#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=DateTimeManager.get_now_utc
#     )
#     updated_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         default=DateTimeManager.get_now_utc,
#         onupdate=DateTimeManager.get_now_utc,
#     )
#     orders: Mapped[list["Order"]] = relationship(
#         "Order",
#         back_populates="products",
#         secondary=order_product,
#     )