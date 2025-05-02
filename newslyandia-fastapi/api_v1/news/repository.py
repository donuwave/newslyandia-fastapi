import datetime
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import News
from .schema import GetNewsResponse, CreateNews


@dataclass
class NewsRepository:
    db_session: AsyncSession

    async def get_news(self):
        stmt = (
            select(News)
            .where(News.deleted_at == None)
            .order_by(News.id.desc())
            .limit(30)
        )
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_news_by_id(self, news_id: int) -> GetNewsResponse:
        query = select(News).where(News.id == news_id)

        session = await self.db_session.execute(query)
        return session.scalar()

    async def create_news_item(self, news_item: CreateNews):
        result = await self.db_session.execute(
            select(News).where(News.deleted_at == None).where(News.url == news_item.url)
        )

        exist = result.scalar_one_or_none()

        if exist:
            return

        print("Создание новости!!!")
        news = News(
            title=news_item.title,
            url=news_item.url,
            text=news_item.text,
            image=news_item.image,
            deleted_at=None,
        )
        self.db_session.add(news)
        await self.db_session.flush()
        await self.db_session.commit()

    async def delete_news(self, news_id: int):
        result = await self.db_session.execute(select(News).where(News.id == news_id))
        news = result.scalar_one_or_none()

        if news:
            news.deleted_at = datetime.datetime.utcnow()
            await self.db_session.commit()
