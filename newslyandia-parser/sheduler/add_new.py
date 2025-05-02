import httpx

from settings import settings


async def add_news(news_item):
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{settings.API_URL}/news", json=news_item)
        r.raise_for_status()
        return r.json()