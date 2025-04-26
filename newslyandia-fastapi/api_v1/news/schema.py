from pydantic import BaseModel


class GetNewsResponse(BaseModel):
    id: int
    image: str
    title: str
    text: str
