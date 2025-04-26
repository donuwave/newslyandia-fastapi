from dataclasses import dataclass

@dataclass
class News:
    id: int
    title: str
    text: str
    image: str
