from contextlib import asynccontextmanager

from fastapi import FastAPI
from telethon import TelegramClient

from config.settings import settings

bot_client = TelegramClient('bot_session', settings.API_ID, settings.API_HASH)

import bot_v1.settings.handler
import bot_v1.news.handler
import bot_v1.contest.handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot_client.start(bot_token=settings.BOT_TOKEN)
    print("🤖 Telegram bot started")

    yield

    print("🛑 Telegram bot stopped")


app = FastAPI(lifespan=lifespan)