from fastapi import APIRouter

from .news import news_router

router = APIRouter()
router.include_router(news_router, prefix="/news", tags=["news"])
