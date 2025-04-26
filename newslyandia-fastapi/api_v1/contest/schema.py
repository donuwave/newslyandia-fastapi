from typing import Optional, List

from pydantic import BaseModel


class ContestBase(BaseModel):
    post_id: int
    discussion_msg_id: int
    commentators: list[int]
    is_active: bool


class ContestCreate(ContestBase):
    class Config:
        orm_mode = True


class ContestRead(ContestBase):
    id: int


class ContestUpdate(BaseModel):
    post_id: Optional[int] = None
    discussion_msg_id: Optional[int] = None
    commentators: Optional[List[int]] = None
