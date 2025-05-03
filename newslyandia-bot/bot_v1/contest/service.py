import random
from dataclasses import dataclass

from bot_v1.contest.api import ServiceContest
from bot_v1.contest.utils import is_subscribed
from config.settings import settings
from main import bot_client
from model_news import Contest


@dataclass
class ContestService:
    service_contest = ServiceContest()

    async def create_giveaway(self, event):
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

        await self.service_contest.create_contest(data=contest)
        await event.respond("✅ Розыгрыш запущен!")

    async def catch_comment(self, event):
        contest = await self.service_contest.fetch_active_contest()

        if contest.discussion_msg_id and event.reply_to_msg_id == contest.discussion_msg_id:
            await self.service_contest.add_commentator(user_id=event.sender_id)

    async def select_winner(self, event):
        contest = await self.service_contest.fetch_active_contest()

        if not contest.post_id or not contest.commentators:
            return await event.respond("❌ Нет активного розыгрыша или участников.")

        success_users = []
        for user_id in contest.commentators:
            if await is_subscribed(user_id):
                success_users.append(user_id)

        if len(success_users) == 0:
            await self.service_contest.finish_contest()

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

        await self.service_contest.finish_contest()