from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from models.news import Base

DATABASE_URL = "postgresql+asyncpg://postgres:qwerty@localhost:5432/"

engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

