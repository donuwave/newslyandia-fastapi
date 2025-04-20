from sqlalchemy import Column, String, Text, Integer

from config.base_model import Base


class News(Base):
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(512), nullable=False)
    url = Column(String(1024), unique=True, nullable=False)
    text = Column(Text, nullable=True)
    image = Column(String(1024), nullable=True)
