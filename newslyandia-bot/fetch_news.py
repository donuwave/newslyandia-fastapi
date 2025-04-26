import httpx
from config import NEWS_API_URL, NEWS_LOCAL_API_URL
from model_news import News


async def fetch_news() -> list[News]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(NEWS_LOCAL_API_URL)
        data = resp.json()
        return [News(**item) for item in data]
