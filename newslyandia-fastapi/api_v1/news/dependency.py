from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api_v1.news.repository import NewsRepository
from api_v1.news.service import NewsService
from config.database import db_helper


async def get_news_repository(
    session: AsyncSession = Depends(db_helper.scoped_session_dependency),
) -> NewsRepository:
    return NewsRepository(db_session=session)


async def get_news_service(
    news_repository: NewsRepository = Depends(get_news_repository),
) -> NewsService:
    return NewsService(news_repository=news_repository)
