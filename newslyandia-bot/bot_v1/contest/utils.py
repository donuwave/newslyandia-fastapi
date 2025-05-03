from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

from config.settings import settings
from main import bot_client


async def is_subscribed(user_id):
    try:
        await bot_client(GetParticipantRequest(channel=settings.CHANNEL_ID, participant=user_id))
        return True
    except UserNotParticipantError:
        return False