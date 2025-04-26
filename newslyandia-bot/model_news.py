from pydantic import BaseModel
from typing import Optional


class News(BaseModel):
    id: int
    title: str
    text: str
    image: str

class Contest(BaseModel):
    post_id: int
    discussion_msg_id: int
    commentators: list[int]
    is_active: bool

    class Config:
        from_attributes = True


class ContestUpdate(BaseModel):
    post_id: Optional[int]
    discussion_msg_id: Optional[int]
    commentators: Optional[list[int]]