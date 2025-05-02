from typing import Annotated, List

from api_v1.news.dependency import get_news_service
from fastapi import APIRouter, Depends

from api_v1.news.schema import GetNewsResponse, CreateNews
from api_v1.news.service import NewsService

router = APIRouter(tags=["news"])


@router.get("", response_model=List[GetNewsResponse])
async def get_news(news_service: Annotated[NewsService, Depends(get_news_service)]):
    return await news_service.get_news()


@router.get("/{news_id}", response_model=GetNewsResponse)
async def get_news_by_id(
    news_id: int, news_service: Annotated[NewsService, Depends(get_news_service)]
):
    return await news_service.get_news_by_id(news_id=news_id)


@router.delete("/{news_id")
async def delete_news_by_id(
    news_id: int, news_service: Annotated[NewsService, Depends(get_news_service)]
):
    return await news_service.delete_news_by_id(news_id=news_id)


@router.post("")
async def create_news_item(
    news_item: CreateNews,
    news_service: Annotated[NewsService, Depends(get_news_service)],
):
    return await news_service.create_news_item(news_item=news_item)
