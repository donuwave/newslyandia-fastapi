import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from fetch_news import fetch_news
from keyboards import news_list_keyboard, preview_keyboard, publish_keyboard
from model_news import News
from utils import build_full_text
from aiogram.fsm.state import StatesGroup, State

class PostStates(StatesGroup):
    waiting_for_edit = State()

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# 📍 Временное хранилище
news_cache: dict[int, News] = {}

@router.message(F.text == "/start")
async def start(message: types.Message):
    await message.answer("👋 Привет! Напиши /news, чтобы посмотреть список новостей.")

@router.message(F.text == "/news")
async def show_news_list(message: types.Message):
    news_list = await fetch_news()
    for news in news_list:
        news_cache[news.id] = news
    await message.answer("📰 Выберите новость:", reply_markup=news_list_keyboard(news_list))

import html

@router.callback_query(F.data.startswith("preview_"))
async def full_view(callback: types.CallbackQuery):
    news_id = int(callback.data.split("_")[1])
    news = news_cache.get(news_id)
    if not news:
        return await callback.message.answer("❌ Новость не найдена")

    safe_text  = html.escape(news.text)
    full = f"\n\n{safe_text}\n\n"
    length = len(safe_text)

    await callback.message.answer_photo(photo=news.image)

    await callback.message.answer(
        f"{full}\n\n— Кол-во символов: <code>{length}</code>",
        parse_mode=ParseMode.HTML,
        reply_markup=preview_keyboard(news_id)
    )

@router.callback_query(F.data.startswith("edit_"))
async def edit_text(callback: types.CallbackQuery, state: FSMContext):
    news_id = int(callback.data.split("_")[1])
    await state.set_state(PostStates.waiting_for_edit)
    await state.update_data(news_id=news_id)
    await callback.message.answer("✏️ Пришли мне изменённый текст новости:")

@router.message(PostStates.waiting_for_edit)
async def process_edit(message: types.Message, state: FSMContext):
    data = await state.get_data()
    news_id = data["news_id"]
    news = news_cache.get(news_id)

    if not news:
        await message.answer("❌ Новости с таким ID не нашлось.")
        return await state.clear()

    # 1) Сохраняем новый текст
    news.text = message.text
    await state.clear()

    # 2) Строим безопасный caption (≤1024 символа)
    caption = (
        f"<b>{html.escape(news.title)}</b>\n\n"
        f"{html.escape(news.text)}\n\n"
    )
    if len(caption) > 1024:
        caption = caption[:1020] + "..."

    # 3) Отправляем превью с фото
    await message.answer_photo(
        photo=news.image,
        caption=caption,
        parse_mode=ParseMode.HTML,
        reply_markup=publish_keyboard(news_id)
    )


@router.callback_query(F.data.startswith("full_"))
async def show_full_text(callback: types.CallbackQuery):
    news_id = int(callback.data.split("_")[1])
    news = news_cache.get(news_id)

    if not news:
        await callback.message.answer("❌ Новость не найдена")
        return

    full_text = build_full_text(news)

    # Отправляем полным текстом
    await callback.message.answer(full_text, parse_mode=ParseMode.HTML)


@router.callback_query(F.data.startswith("publish_"))
async def publish_news(callback: types.CallbackQuery):
    news_id = int(callback.data.split("_")[1])
    news = news_cache.get(news_id)

    if not news:
        await callback.message.answer("❌ Новость не найдена")
        return

    caption = f"<b>{html.escape(news.title)}</b>\n\n{html.escape(news.text)}\n\n"
    caption = caption[:1020] + "..." if len(caption) > 1024 else caption

    try:
        await bot.send_photo(
            chat_id='-1002638451304',
            photo=news.image,
            caption=caption,
            parse_mode='HTML'  # Только если ты уверен, что весь текст валидный
        )
        await callback.message.answer("✅ Новость опубликована!")
    except Exception as e:
        await callback.message.answer(f"💥 Ошибка публикации: {e}")


async def main():
    print("🤖 Бот запущен")
    # цикл, чтобы автоматически восстанавливать polling
    while True:
        try:
            # skip_updates=True сбросит старые апдейты при рестарте
            await dp.start_polling(bot, skip_updates=True)
            break  # если вдруг start_polling завершился без ошибок
        except TelegramNetworkError as e:
            print(f"🌐 Сетевая ошибка, перезапуск polling через 1 сек: {e}")
            await asyncio.sleep(1)
        except Exception as e:
            # на всякий случай ловим всё остальное
            print(f"❗ Непредвиденная ошибка в polling: {e}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
