import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api_v1 import router as router_v1
from config.database import init_db
from scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    loop = asyncio.get_running_loop()
    scheduler = start_scheduler(loop=loop)
    app.state.scheduler = scheduler
    print("🚀 Планировщик запущен")

    yield

    print("🛑 Остановка планировщика")


app = FastAPI(lifespan=lifespan)
app.include_router(router=router_v1, prefix="/api/v1")
