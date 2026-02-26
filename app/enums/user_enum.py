from enum import StrEnum, unique


@unique
class UserStatusEnum(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


@unique
class UserRoleEnum(StrEnum):
    ADMIN = "admin"
