import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db import init_db
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    loop = asyncio.get_running_loop()
    scheduler = start_scheduler(loop=loop)
    app.state.scheduler = scheduler
    print("🚀 Планировщик запущен")

    yield  # <-- здесь работает приложение

    print("🛑 Остановка планировщика")


app = FastAPI(lifespan=lifespan)
