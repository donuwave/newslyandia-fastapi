from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def news_list_keyboard(news_list: list):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=news.title[:30], callback_data=f"preview_{news.id}")]
        for news in news_list
    ])
    return kb

def preview_keyboard(news_id: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_{news_id}"),
            InlineKeyboardButton(text="📢 Опубликовать", callback_data=f"publish_{news_id}")
        ]
    ])

def publish_keyboard(news_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Опубликовать",
                    callback_data=f"publish_{news_id}"
                )
            ]
        ]
    )