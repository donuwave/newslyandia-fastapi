import html
import random
import re
from telethon import TelegramClient, events, Button
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest

from fetch_contest import ServiceContest
from fetch_news import ServiceNews
from model_news import Contest
from settings import settings
from utils import build_full_text

bot_client = TelegramClient('bot_session', settings.API_ID, settings.API_HASH).start(bot_token=settings.BOT_TOKEN)

max_size = 4096
name_chanel = "@newslyandia"

user_states: dict[int, dict] = {}
PROMO_FOOTER = "<b>🔔 Подписывайтесь на наш канал, чтобы не пропустить важные новости. </b>"

service_news = ServiceNews()
service_contest = ServiceContest()


@bot_client.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    await event.respond("👋 Привет! Напиши /news, чтобы посмотреть список новостей.")

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

def safe_chunks(text: str, step: int = max_size):
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
        user_states.pop(event.sender_id, None)

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

    st = user_states.get(event.sender_id)

    caption = (
        f"<b>{html.escape(st['title'])}</b>\n\n"
        f"{html.escape(st['text'])}\n\n"
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

# Проверка подписки
async def is_subscribed(user_id):
    try:
        await bot_client(GetParticipantRequest(channel=settings.CHANNEL_ID, participant=user_id))
        return True
    except UserNotParticipantError:
        return False


# Выбор победителя
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

# ——————————————————————————————————————————————
def main():
    print("🤖 Бот (Telethon) запущен")
    bot_client.run_until_disconnected()


if __name__ == "__main__":
    main()
