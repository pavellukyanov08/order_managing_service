from pydantic import Field

from app.common.schemas import CamelDTO


class MessageDTO(CamelDTO):
    message: str = Field(
        ..., min_length=1, max_length=256, description="Some message"
    )
