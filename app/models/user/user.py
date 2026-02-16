from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.enums import UserStatusEnum
from app.utils import DateTimeManager


class User(Base):
    __tablename__ = "user"

    sid: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(length=100), index=True, unique=True, comment="Email of user")
    fullname: Mapped[str] = mapped_column(index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(
        comment="Hashed password of user"
    )
    status: Mapped[UserStatusEnum] = mapped_column(
        Enum(
            UserStatusEnum,
            name="userstatusenum",
            values_callable=lambda x: [e.value for e in x],
        ),
        default=UserStatusEnum.ACTIVE,
        comment="Status of user")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=DateTimeManager.get_now_utc,
        onupdate=DateTimeManager.get_now_utc,
    )

    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
