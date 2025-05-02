import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sheduler.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_running_loop()
    scheduler = start_scheduler(loop=loop)
    app.state.scheduler = scheduler
    print("🚀 Планировщик запущен")
    yield
    print("🛑 Остановка планировщика")


app = FastAPI(lifespan=lifespan)