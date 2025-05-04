from dataclasses import dataclass, field

from telethon import Button
from telethon.extensions import html

from bot_v1.news.api import ServiceNews
from bot_v1.news.utils import build_full_text, safe_chunks
from config.settings import settings
from main import bot_client


name_chanel = "@newslyandia"


@dataclass
class NewsServie:
    service_news = ServiceNews()
    user_states: dict[int, dict] = field(default_factory=dict)

    async def show_news_list(self, event):
        news_list = await self.service_news.fetch_news()

        if not news_list:
            await event.respond("❌ Нет доступных новостей.")
            return

        buttons = [
            [Button.inline(str((news.title or f"#{news.id}")[:50]), data=f"preview_{news.id}".encode())]
            for news in news_list
        ]

        await event.respond("📰 Выберите новость:", buttons=buttons)

    async def preview_news_item(self, event):
        await event.answer()

        news_id = int(event.data.decode().split("_")[1])

        try:
            news_item = await self.service_news.fetch_news_item(news_id)
        except Exception:
            return await event.respond("❌ Не удалось получить новость.", alert=True)

        safe_text = html.escape(news_item.text)
        full = f"\n\n{safe_text}\n\n"
        length = len(safe_text)

        await bot_client.send_file(event.chat_id, file=news_item.image)

        keyboard = [
            [Button.inline("📖 Полный текст", data=f"full_{news_id}")],
            [Button.inline("✏️ Редактировать", data=f"edit_{news_id}")],
            [Button.inline("🚀 Опубликовать", data=f"publish_{news_id}")]
        ]

        await bot_client.send_message(
            event.chat_id,
            f"{full}\n\n— Кол-во символов: <code>{length}</code>",
            parse_mode="html",
            buttons=keyboard
        )

    async def fulltext_news_item(self, event):
        await event.answer()
        news_id = int(event.data.decode().split("_")[1])

        try:
            news_item = await self.service_news.fetch_news_item(news_id)
        except Exception:
            return await event.respond("❌ Не удалось получить новость.", alert=True)
        if not news_item:
            return await event.respond("❌ Новость не найдена.", alert=True)

        full = build_full_text(news_item)

        entity = await bot_client.get_entity(event.chat_id)
        if getattr(entity, "bot", False):
            return await event.respond("❌ Боту нельзя прислать длинный текст.", alert=True)

        for chunk in safe_chunks(full):
            try:
                await bot_client.send_message(event.chat_id, chunk, parse_mode="html")
            except Exception:
                await bot_client.send_message(event.chat_id, f"<code>{html.escape(chunk)}</code>", parse_mode="html")

    async def edit_start_news_item(self, event):
        await event.answer()
        news_id = int(event.data.decode().split("_")[1])

        # Уберём шаг с заголовком — сразу переходим к редактированию тела
        self.user_states[event.sender_id] = {
            "mode": "editing",
            "news_id": news_id,
            "step": "body",
            "body": "",
        }
        await bot_client.send_message(
            event.chat_id,
            "📝 Отправьте *новый текст* поста.",
            parse_mode="Markdown"
        )

    async def edit_receive_news_item(self, event):
        st = self.user_states.get(event.sender_id)
        if not st or st.get("mode") != "editing":
            return

        txt = event.raw_text.strip()
        if not txt:
            return await event.respond("❌ Текст не может быть пустым.")

        # Записываем новый body и сразу показываем превью с промо
        st["body"] = txt
        news = await self.service_news.fetch_news_item(st["news_id"])
        if not news:
            return await event.respond("❌ Новость не найдена.", alert=True)

        news.text = st["body"]

        caption = (
            f"{html.escape(news.text)}\n\n"
            f"{name_chanel}"
        )
        if len(caption) > 1024:
            caption = caption[:1020] + "…"

        kb = [
            [Button.inline("📖 Полный текст", data=f"full_{news.id}")],
            [Button.inline("🚀 Опубликовать", data=f"publish_{news.id}")]
        ]

        if news.image:
            await bot_client.send_file(
                event.chat_id,
                news.image,
                caption=caption,
                parse_mode="html",
                buttons=kb
            )
        else:
            await bot_client.send_message(
                event.chat_id,
                caption,
                parse_mode="html",
                buttons=kb
            )

    async def publish_news_item(self, event):
        await event.answer()
        news_id = int(event.data.decode().split("_")[1])

        try:
            news = await self.service_news.fetch_news_item(news_id)
        except Exception:
            return await event.respond("❌ Не удалось получить новость.", alert=True)

        st = self.user_states.pop(event.sender_id, None)

        body = (st and st.get("body")) or news.text

        caption = (
            f"{html.escape(body)}\n\n"
            f"{name_chanel}"
        )
        if len(caption) > 1024:
            caption = caption[:1020] + "…"

        await bot_client.send_file(
            settings.CHANNEL_ID,
            news.image,
            caption=caption,
            parse_mode="html"
        )

        await event.respond("✅ Новость опубликована!")
