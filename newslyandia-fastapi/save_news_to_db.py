from db import AsyncSessionLocal
from sqlalchemy import select

from models.news import News

async def save_news_to_db(news_list: list[dict]):
    async with AsyncSessionLocal() as session:
        for item in news_list:
            result = await session.execute(
                select(News).where(News.url == item["url"])
            )
            exists = result.scalar_one_or_none()
            if exists:
                continue

            news = News(
                title=item["title"],
                url=item["url"],
                text=item["content"],
                image=item["img"]
            )
            session.add(news)
        await session.commit()
