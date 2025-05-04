import re

from telethon import events

from bot_v1.news.api import ServiceNews
from bot_v1.news.service import NewsServie
from config.settings import settings
from main import bot_client

service_news = ServiceNews()

user_states: dict[int, dict] = {}
PROMO_FOOTER = "<b>🔔 Подписывайтесь на наш канал, чтобы не пропустить важные новости. </b>"
name_chanel = "@newslyandia"

news_service = NewsServie()

@bot_client.on(events.NewMessage(from_users=settings.CHANEL_ADMINS, pattern=r'^/news$'))
async def show_news_list(event):
    await news_service.show_news_list(event)

@bot_client.on(events.CallbackQuery(data=re.compile(b"^preview_\\d+$")))
async def preview_handler(event):
    await news_service.preview_news_item(event)


@bot_client.on(events.CallbackQuery(data=re.compile(b"^full_\\d+$")))
async def fulltext_handler(event):
    await news_service.fulltext_news_item(event)

@bot_client.on(events.CallbackQuery(data=re.compile(b"^edit_\\d+$")))
async def edit_start_handler(event):
    await news_service.edit_start_news_item(event)

@bot_client.on(events.NewMessage(from_users=settings.CHANEL_ADMINS))
async def edit_receive_handler(event):
    await news_service.edit_receive_news_item(event)


@bot_client.on(events.CallbackQuery(data=re.compile(b"^publish_\\d+$")))
async def publish_handler(event):
    await news_service.publish_news_item(event)
