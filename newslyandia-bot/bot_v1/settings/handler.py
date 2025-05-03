from telethon import events

from main import bot_client


@bot_client.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    await event.respond("👋 Привет! Напиши /news, чтобы посмотреть список новостей.")