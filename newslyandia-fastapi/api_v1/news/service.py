from dataclasses import dataclass
from api_v1.news.repository import NewsRepository


@dataclass
class NewsService:
    news_repository: NewsRepository

    async def get_news(self):
        return await self.news_repository.get_news()

    async def get_news_by_id(self, news_id: int):
        return await self.news_repository.get_news_by_id(news_id=news_id)

    async def delete_news_by_id(self, news_id: int):
        return await self.news_repository.delete_news(news_id=news_id)
