from telethon import events
from bot_v1.contest.service import ContestService
from main import bot_client
from config.settings import settings

contest_service = ContestService()


@bot_client.on(events.NewMessage(pattern=r'^/create_giveaway$'))
async def create_giveaway_handler(event):
    await contest_service.create_giveaway(event)


@bot_client.on(events.NewMessage(chats=settings.GROUP_CHAT_ID))
async def catch_comment_handler(event):
    await contest_service.catch_comment(event)


@bot_client.on(events.NewMessage(pattern=r'^/select_winner$'))
async def select_winner_handler(event):
    await contest_service.select_winner(event)