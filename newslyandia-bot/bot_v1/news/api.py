import time
from typing import Optional, Any, List

import httpx
from model_news import News
from config.settings import settings

TTL = 300

class ServiceNews:
    _cache: dict[str, tuple[float, Any]] = {}
    base_url: str = settings.API_URL

    @classmethod
    async def _get_json(self, url: str) -> Any:
        ts, data = self._cache.get(url, (0, None))
        if time.time() - ts < TTL:
            return data

        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()

        self._cache[url] = (time.time(), data)
        return data


    @classmethod
    async def fetch_news(self) -> List[News]:
        raw = await self._get_json(f"{self.base_url}/news")
        return [News(**item) for item in raw]

    @classmethod
    async def fetch_news_item(self, news_id: int) -> News:
        raw = await self._get_json(f"{self.base_url}/news/{news_id}")
        return News(**raw)


    @classmethod
    def invalidate(self, news_id: Optional[int] = None) -> None:
        if news_id is None:
            self._cache.clear()
        else:
            self._cache.pop(f"{self.base_url}/news/{news_id}", None)
