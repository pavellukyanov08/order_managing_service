from uuid import UUID
from pydantic import BaseModel, Field


class CreateOrderEvent(BaseModel):
    object: str = Field(...)
    customer: UUID = Field()
