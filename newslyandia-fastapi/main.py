import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db import init_db, get_session
from models import News
from scheduler import start_scheduler

router = APIRouter()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    loop = asyncio.get_running_loop()
    scheduler = start_scheduler(loop=loop)
    app.state.scheduler = scheduler
    print("🚀 Планировщик запущен")

    yield  # <-- здесь работает приложение

    print("🛑 Остановка планировщика")

@router.get("/news")
async def get_news(session: AsyncSession = Depends(get_session)):
    stmt = (
        select(News)
        .order_by(News.id.desc())  # или .order_by(desc(News.created_at)) если есть дата
        .limit(30)
    )
    result = await session.execute(stmt)
    return result.scalars().all()

app = FastAPI(lifespan=lifespan)
app.include_router(router)