from pydantic import Field, BaseModel

from app.common.schemas import CamelDTO, EmailDTO
from ..token import TokenPair


class AuthLogin(CamelDTO, EmailDTO):
    password: str = Field(
        ...,
        max_length=256,
        description="User password",
    )


class AuthLoginResult(BaseModel):
    tokens: TokenPair | None = None
