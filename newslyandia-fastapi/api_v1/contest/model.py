from sqlalchemy import Column, Integer, ARRAY, Boolean, BIGINT

from config.base_model import Base


class Contest(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer)
    discussion_msg_id = Column(Integer)
    commentators = Column(ARRAY(BIGINT), nullable=False, default=[])
    is_active = Column(Boolean)
