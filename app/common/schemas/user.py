from datetime import datetime
from uuid import UUID
from pydantic import Field
from .base import EmailDTO

from app.enums import UserStatusEnum, UserRoleEnum
from app.utils.normalize_datetime import NormalizeDateTime


class UserDTO(NormalizeDateTime, EmailDTO):
    sid: UUID = Field(..., description="SID of user")
    fullname: str = Field(..., description="First, middle, last of user")
    status: UserStatusEnum = Field(default=UserStatusEnum.ACTIVE, description="Status of user")
    role: UserRoleEnum | None = Field(default=None, description="Role of user")
    hashed_password: str = Field(..., description="Password of user")
    created_at: datetime = Field(..., description="User created at")
    updated_at: datetime = Field(..., description="User updated at")
