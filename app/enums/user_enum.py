from enum import StrEnum, unique


@unique
class UserRoleEnum(StrEnum):
    USER = "Пользователь"
    ADMIN = "Администратор"
