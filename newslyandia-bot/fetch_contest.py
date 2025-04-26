import time
from typing import Any, List

import httpx

from model_news import Contest, ContestUpdate
from settings import settings

TTL = 300

class ServiceContest:
    _cache: dict[str, tuple[float, Any]] = {}
    base_url: str = settings.API_URL

    @classmethod
    async def _get_json(cls, url: str) -> Any:
        ts, data = cls._cache.get(url, (0, None))
        if time.time() - ts < TTL:
            return data

        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            r.raise_for_status()
            data = r.json()

        cls._cache[url] = (time.time(), data)
        return data

    @classmethod
    async def _patch_json(cls, url: str, payload: ContestUpdate) -> Any:
        async with httpx.AsyncClient() as client:
            r = await client.patch(url, json=payload)
            r.raise_for_status()
            return r.json()

    @classmethod
    async def _post_json(cls, url: str, payload: any) -> Any:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            return r.json()

    @classmethod
    async def _post_json_not_json(cls, url: str) -> Any:
        async with httpx.AsyncClient() as client:
            r = await client.post(url)
            r.raise_for_status()
            return r.json()

    @classmethod
    async def fetch_active_contest(cls) -> Contest:
        response = await cls._post_json_not_json(f"{cls.base_url}/contest/active")
        return Contest(**response)

    @classmethod
    async def create_contest(cls, data: Contest):
        return await cls._post_json(f"{cls.base_url}/contest", data.model_dump())

    @classmethod
    async def add_commentator(cls, user_id: int):
        return await cls._post_json_not_json(
            f"{cls.base_url}/contest/active/add_commentator/{user_id}"
        )

    @classmethod
    async def finish_contest(cls):
        async with httpx.AsyncClient() as client:
            await client.post(f"{cls.base_url}/contest/deactivate")