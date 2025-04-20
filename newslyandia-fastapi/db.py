from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from config.settings import app_settings
from models.news import Base


engine = create_async_engine(app_settings.db_url, echo=True)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session
