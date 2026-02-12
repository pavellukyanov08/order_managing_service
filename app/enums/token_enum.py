from enum import StrEnum


class TokenTypeEnum(StrEnum):
    BEARER = "Bearer"
    ACCESS = "access"
    REFRESH = "refresh"


