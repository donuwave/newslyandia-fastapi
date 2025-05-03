import re

from telethon import events, Button
from telethon.extensions import html

from bot_v1.news.api import ServiceNews
from config.settings import settings
from main import bot_client
from bot_v1.news.utils import build_full_text

service_news = ServiceNews()

user_states: dict[int, dict] = {}
PROMO_FOOTER = "<b>🔔 Подписывайтесь на наш канал, чтобы не пропустить важные новости. </b>"
name_chanel = "@newslyandia"


@bot_client.on(events.NewMessage(pattern=r'^/news$'))
async def show_news_list(event):
    news_list = await service_news.fetch_news()

    if not news_list:
        await event.respond("❌ Нет доступных новостей.")
        return

    buttons = [
        [Button.inline(str((news.title or f"#{news.id}")[:50]), data=f"preview_{news.id}".encode())]
        for news in news_list
    ]

    await event.respond("📰 Выберите новость:", buttons=buttons)

@bot_client.on(events.CallbackQuery(data=re.compile(b"^preview_\\d+$")))
async def preview_handler(event):
    await event.answer()

    news_id = int(event.data.decode().split("_")[1])

    try:
        news_item = await service_news.fetch_news_item(news_id)
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

def safe_chunks(text: str, step: int = 4096):
    for i in range(0, len(text), step):
        yield text[i:i + step]

@bot_client.on(events.CallbackQuery(data=re.compile(b"^full_\\d+$")))
async def fulltext_handler(event):
    await event.answer()
    news_id = int(event.data.decode().split("_")[1])

    try:
        news_item = await service_news.fetch_news_item(news_id)
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

@bot_client.on(events.CallbackQuery(data=re.compile(b"^edit_\\d+$")))
async def edit_start_handler(event):
    await event.answer()
    news_id = int(event.data.decode().split("_")[1])

    user_states[event.sender_id] = {
        "mode":    "editing",
        "news_id": news_id,
        "step":    "title",
        "title":   "",
        "body":    "",
    }
    await bot_client.send_message(
        event.chat_id,
        "✏️ Отправьте *новый заголовок* 👇",
        parse_mode="Markdown"
    )

@bot_client.on(events.NewMessage())
async def edit_receive_handler(event):
    st = user_states.get(event.sender_id)
    if not st or st.get("mode") != "editing":
        return

    txt = event.raw_text.strip()

    if st["step"] == "title":
        if not txt:
            return await event.respond("❌ Заголовок не может быть пустым.")
        st["title"] = txt
        st["step"] = "body"
        return await event.respond("📝 Отлично! Теперь пришлите *основной текст* поста.", parse_mode="Markdown")

    if st["step"] == "body":
        if not txt:
            return await event.respond("❌ Текст не может быть пустым.")
        st["body"] = txt
        await show_preview_after_edit(event, st)

async def show_preview_after_edit(event, st):
    news = await service_news.fetch_news_item(st["news_id"])
    if not news:
        return await event.respond("❌ Новость не найдена.")

    news.title = st["title"]
    news.text  = st["body"]

    caption = (
        f"<b>{html.escape(news.title)}</b>\n\n"
        f"{html.escape(news.text)}\n\n"
        f"{PROMO_FOOTER}\n\n"
        f"{name_chanel}"
    )
    if len(caption) > 1024:
        caption = caption[:1020] + "…"

    kb = [
        [Button.inline("📖 Полный текст", data=f"full_{news.id}")],
        [Button.inline("🚀 Опубликовать", data=f"publish_{news.id}")]
    ]

    if news.image:
        await bot_client.send_file(event.chat_id, news.image,
                                   caption=caption, parse_mode="html", buttons=kb)
    else:
        await bot_client.send_message(event.chat_id, caption,
                                      parse_mode="html", buttons=kb)


@bot_client.on(events.CallbackQuery(data=re.compile(b"^publish_\\d+$")))
async def publish_handler(event):
    await event.answer()

    news_id = int(event.data.decode().split("_")[1])

    try:
        news = await service_news.fetch_news_item(news_id)
    except Exception:
        return await event.respond("❌ Не удалось получить новость.", alert=True)

    st = user_states.pop(event.sender_id, None)

    title = (st and st.get("title")) or news.title
    body  = (st and (st.get("body") or st.get("text"))) or news.text

    caption = (
        f"<b>{html.escape(title)}</b>\n\n"
        f"{html.escape(body)}\n\n"
        f"{PROMO_FOOTER}\n\n"
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
