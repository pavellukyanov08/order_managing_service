from pydantic.alias_generators import to_camel
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict


class CamelDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=to_camel,
    )


class EmailDTO(BaseModel):
    email: EmailStr = Field(..., description="Email of user")

    @field_validator("email", mode="after")
    def validate_email(cls, v: str) -> str:
        return v.strip().lower()
