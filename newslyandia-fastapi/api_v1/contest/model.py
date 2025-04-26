from sqlalchemy import Column, Integer

from config.base_model import Base


class Contest(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column()
