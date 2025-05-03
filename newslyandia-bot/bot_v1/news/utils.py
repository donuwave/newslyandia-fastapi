from model_news import News
import html


MAX_CAPTION = 1024

def build_full_text(news: News) -> str:
    safe_title = html.escape(news.title)
    safe_text = html.escape(news.text)

    return f"<b>{safe_title}</b>\n\n{safe_text}\n\n"
