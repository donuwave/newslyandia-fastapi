from contextlib import asynccontextmanager
from fastapi import FastAPI
from api_v1 import router as router_v1


@asynccontextmanager
async def lifespan():
    yield


app = FastAPI()
app.include_router(router=router_v1, prefix="/api/v1")
