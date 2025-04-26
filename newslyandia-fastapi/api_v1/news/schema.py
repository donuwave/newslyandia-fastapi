from typing import Optional

from pydantic import BaseModel


class GetNewsResponse(BaseModel):
    id: int
    image: Optional[str] = None
    title: str
    text: str
