import random

from telethon import events
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

from bot_v1.contest.api import ServiceContest
from main import bot_client
from model_news import Contest
from config.settings import settings

service_contest = ServiceContest()

@bot_client.on(events.NewMessage(pattern=r'^/create_giveaway$'))
async def create_giveaway_handler(event):
    post = await bot_client.send_message(
        settings.CHANNEL_ID,
        "🎉 <b>РОЗЫГРЫШ!</b> 🎉\n"
        "💰 <b>Приз:</b> 3000 ₽ на карту или любую платёжную систему\n"
        "⏳ <b>Итоги:</b> 3 мая\n\n"
        "1️⃣ Подпишитесь на наш канал\n"
        "2️⃣ Оставьте <b>любой</b> комментарий под этим постом\n"
        "3️⃣ Дождитесь финального поста — победитель выбирается случайно\n\n"
        "👇 <b>Комментируйте прямо сейчас!</b>",
        parse_mode="html"
    )

    discussion_msg = await bot_client.send_message(
        settings.GROUP_CHAT_ID,
        f"🗨️ Обсуждение к посту №{post.id}."
    )
    await bot_client.delete_messages(
        entity=settings.GROUP_CHAT_ID,
        message_ids=discussion_msg.id
    )

    contest = Contest(post_id=post.id, discussion_msg_id=discussion_msg.id + 1, commentators=[], is_active=True)

    await service_contest.create_contest(data=contest)
    await event.respond("✅ Розыгрыш запущен!")

@bot_client.on(events.NewMessage(chats=settings.GROUP_CHAT_ID))
async def catch_comment_handler(event):
    contest = await service_contest.fetch_active_contest()

    if contest.discussion_msg_id and event.reply_to_msg_id == contest.discussion_msg_id:
        await service_contest.add_commentator(user_id=event.sender_id)

async def is_subscribed(user_id):
    try:
        await bot_client(GetParticipantRequest(channel=settings.CHANNEL_ID, participant=user_id))
        return True
    except UserNotParticipantError:
        return False


@bot_client.on(events.NewMessage(pattern=r'^/select_winner$'))
async def select_winner_handler(event):
    contest = await service_contest.fetch_active_contest()

    if not contest.post_id or not contest.commentators:
        return await event.respond("❌ Нет активного розыгрыша или участников.")

    success_users = []
    for user_id in contest.commentators:
        if await is_subscribed(user_id):
            success_users.append(user_id)

    if len(success_users) == 0:
        await service_contest.finish_contest()

        try:
            await bot_client.delete_messages(settings.CHANNEL_ID, contest.post_id)
        except Exception as e:
            print(f"Ошибка при удалении поста: {e}")

        return await event.respond("❌ Нет ни одного подписчика.")

    winner_id = random.choice(success_users)
    user = await bot_client.get_entity(winner_id)
    display_name = (
        user.username or
        " ".join(filter(None, [getattr(user, "first_name", ""), getattr(user, "last_name", "")])) or
        "Пользователь"
    )

    try:
        await bot_client.delete_messages(settings.CHANNEL_ID, contest.post_id)
    except Exception as e:
        print(f"Ошибка при удалении поста: {e}")

    text = (
        "🏆 РОЗЫГРЫШ ЗАВЕРШЁН!\n\n"
        f"🎉 Победитель: <a href='tg://user?id={winner_id}'>{display_name}</a>\n\n"
        "Спасибо всем за участие!"
    )
    await bot_client.send_message(settings.CHANNEL_ID, text, parse_mode="html")

    await service_contest.finish_contest()