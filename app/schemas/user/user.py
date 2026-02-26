from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    first_name: str = Field(..., description="First name of user")
    last_name: str = Field(..., description="Last name of user")
    middle_name: str = Field(..., description="Middle name of user")
    email: EmailStr = Field(..., description="Email of user")
    password: str = Field(..., description="Password of user")
    confirm_password: str = Field(..., description="Confirm password of user")

