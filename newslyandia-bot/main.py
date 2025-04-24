import html
import random
import re
from telethon import TelegramClient, events, Button
from telethon.errors import UserNotParticipantError
from telethon.tl.functions.channels import GetParticipantRequest
from telethon.tl.functions.messages import GetDiscussionMessageRequest
from telethon.utils import get_peer_id
from config import API_ID, API_HASH, CHANNEL_ID, BOT_TOKEN
from fetch_news import fetch_news
from model_news import News
from utils import build_full_text

client = TelegramClient("user_session", API_ID, API_HASH).start()
bot_client = TelegramClient('bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

max_size = 4096

news_cache: dict[int, News] = {}
user_states: dict[int, dict] = {}
commentators: set[int] = set()
POST_ID = None
DISCUSSION_CHAT_ID = None
DISCUSSION_MSG_ID = None
PROMO_FOOTER = "<b>🔔 Подписывайтесь на наш канал, чтобы не пропустить важные новости. </b>"


@client.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    await event.respond("👋 Привет! Напиши /news, чтобы посмотреть список новостей.")

@bot_client.on(events.NewMessage(pattern=r'^/news$'))
async def show_news_list(event):
    news_list = await fetch_news()
    for news in news_list:
        news_cache[news.id] = news

    buttons = [
        [Button.inline((news.title or f"#{news.id}")[:50], data=f"preview_{news.id}")]
        for news in news_list
    ]

    await event.respond("📰 Выберите новость:", buttons=buttons)


@bot_client.on(events.CallbackQuery(data=re.compile(b"^preview_\\d+$")))
async def preview_handler(event):
    await event.answer()

    news_id = int(event.data.decode().split("_")[1])
    news = news_cache.get(news_id)
    if not news:
        return await event.respond("❌ Новость не найдена.", alert=True)

    safe_text = html.escape(news.text)
    full = f"\n\n{safe_text}\n\n"
    length = len(safe_text)

    await bot_client.send_file(event.chat_id, file=news.image)

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
    news = news_cache.get(news_id)
    if not news:
        return await event.respond("❌ Новость не найдена.", alert=True)

    full = build_full_text(news)

    entity = await client.get_entity(event.chat_id)
    if getattr(entity, "bot", False):
        return await event.respond("❌ Боту нельзя прислать длинный текст.", alert=True)

    for chunk in safe_chunks(full):
        try:
            await bot_client.send_message(event.chat_id, chunk, parse_mode="html")
        except Exception:
            await client.send_message(event.chat_id, f"<code>{html.escape(chunk)}</code>", parse_mode="html")


@bot_client.on(events.CallbackQuery(data=re.compile(b"^edit_\\d+$")))
async def edit_start_handler(event):
    await event.answer()
    news_id = int(event.data.decode().split("_")[1])
    user_states[event.sender_id] = {"state": "editing", "news_id": news_id, "step": "waiting"}
    await bot_client.send_message(
        event.chat_id,
        "✏️ Пришлите *одним* сообщением новый контент.\n\n"
        "Формат:\n"
        "1-я строка — заголовок\n"
        "пустая строка\n"
        "2-й блок — основной текст\n"
        "пустая строка (необязательно)\n"
        "3-й блок — «подвал» (необязательно)",
        parse_mode="Markdown"
    )

@bot_client.on(events.NewMessage())
async def edit_receive_handler(event):
    state = user_states.get(event.sender_id)
    if not state or state.get("state") != "editing":
        return

    news_id = state["news_id"]
    news = news_cache.get(news_id)
    if not news:
        user_states.pop(event.sender_id, None)
        return

    parts = event.raw_text.split("\n\n")
    if len(parts) < 2:
        await bot_client.send_message(
            event.chat_id,
            "❌ Неверный формат. Нужен хотя бы заголовок + текст."
        )
        return

    new_title = parts[0].strip()
    new_body  = parts[1].strip()
    user_footer = parts[2].strip() if len(parts) >= 3 else ""

    # обновляем объект News
    news.title = new_title
    news.text  = new_body

    # итоговый футер: промо + пользователь
    if user_footer:
        news.footer = f"\n\n{PROMO_FOOTER}\n\n{user_footer}"
    else:
        news.footer = f"\n\n{PROMO_FOOTER}"

    caption = (
        f"<b>{html.escape(news.title)}</b>\n\n"
        f"{html.escape(news.text)}"
        f"{news.footer}"
    )
    if len(caption) > 1024:
        caption = caption[:1020] + "…"

    kb = [
        [Button.inline("📖 Полный текст", data=f"full_{news_id}")],
        [Button.inline("🚀 Опубликовать", data=f"publish_{news_id}")]
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

    user_states.pop(event.sender_id, None)


@bot_client.on(events.CallbackQuery(data=re.compile(b"^publish_\\d+$")))
async def publish_handler(event):
    await event.answer()

    news_id = int(event.data.decode().split("_")[1])
    news = news_cache.get(news_id)
    if not news:
        return await event.respond("❌ Новость не найдена.", alert=True)

    footer = getattr(news, "footer", "")
    caption = (
        f"<b>{html.escape(news.title)}</b>\n\n"
        f"{html.escape(news.text)}"
        f"{footer}"        # ← вот эта строка
    )
    if len(caption) > 1024:
        caption = caption[:1020] + "…"

    await client.send_file(
        CHANNEL_ID,
        news.image,
        caption=caption,
        parse_mode="html"
    )

    await event.respond("✅ Новость опубликована!")



@client.on(events.NewMessage(pattern=r'^/create_giveaway$'))
async def create_giveaway_handler(event):
    global POST_ID, DISCUSSION_CHAT_ID, DISCUSSION_MSG_ID
    post = await client.send_message(
        CHANNEL_ID,
        "🎉 РОЗЫГРЫШ НАЧАЛСЯ!\n\n"
        "Условия участия:\n"
        "1️⃣ Подпишитесь на канал.\n"
        "2️⃣ Оставьте комментарий под этим постом.\n\n"
        "Победитель будет выбран случайным образом!"
    )
    POST_ID = post.id
    commentators.clear()

    result = await client(GetDiscussionMessageRequest(
        peer=CHANNEL_ID,
        msg_id=POST_ID
    ))
    discussion_msg = result.messages[1] if len(result.messages) > 1 else result.messages[0]
    DISCUSSION_CHAT_ID = get_peer_id(discussion_msg.peer_id)
    DISCUSSION_MSG_ID = discussion_msg.id

    await event.respond("✅ Пост с розыгрышем опубликован!")

@client.on(events.NewMessage())
async def catch_comment_handler(event):
    if (event.chat_id == DISCUSSION_CHAT_ID and
        event.reply_to_msg_id == DISCUSSION_MSG_ID):
        commentators.add(event.sender_id)

async def is_subscribed(user_id):
    try:
        await client(GetParticipantRequest(channel=CHANNEL_ID, participant=user_id))
        return True
    except UserNotParticipantError:
        return False

async def filter_subscribed_users():
    global commentators

    subscribed_users = []
    for user_id in commentators:
        if await is_subscribed(user_id):
            subscribed_users.append(user_id)
    return subscribed_users


@client.on(events.NewMessage(pattern=r'^/select_winner$'))
async def select_winner_handler(event):
    global POST_ID, DISCUSSION_CHAT_ID, DISCUSSION_MSG_ID
    if not POST_ID or not commentators:
        return await event.respond("❌ Нет активного розыгрыша или участников.")

    success_users = await filter_subscribed_users()

    if len(success_users) == 0:
        return await event.respond("❌ Нет ни одного подписчика.")

    winner_id = random.choice(success_users)
    user = await client.get_entity(winner_id)
    display_name = (
        user.username
        or " ".join(filter(None, [getattr(user, "first_name", ""), getattr(user, "last_name", "")]))
        or "Пользователь"
    )

    try:
        await client.delete_messages(CHANNEL_ID, POST_ID)
    except:
        pass

    text = (
        "🏆 РОЗЫГРЫШ ЗАВЕРШЁН!\n\n"
        f"🎉 Победитель: <a href='tg://user?id={winner_id}'>{display_name}</a>\n\n"
        "Спасибо всем за участие!"
    )
    await client.send_message(CHANNEL_ID, text, parse_mode="html")

    # сброс
    POST_ID = None
    DISCUSSION_CHAT_ID = None
    DISCUSSION_MSG_ID = None
    commentators.clear()

# ——————————————————————————————————————————————
def main():
    print("🤖 Бот (Telethon) запущен")
    client.run_until_disconnected()
    bot_client.run_until_disconnected()

if __name__ == "__main__":
    main()
