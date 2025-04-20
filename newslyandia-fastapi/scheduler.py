import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from parse.parse_news_dot_ru import parse_news_dot_ru
from parse.parse_news_dze import parse_news_gazeta
from save_news_to_db import save_news_to_db

job_lock = asyncio.Lock()

async def scheduled_job():
    if job_lock.locked():
        print("⚠️ Предыдущая задача ещё работает, пропускаем запуск.")
        return


    async with job_lock:
        try:
            news = []

            news_dot_ru = await parse_news_dot_ru()
            parse_gazeta = await parse_news_gazeta()

            news.extend(news_dot_ru)
            news.extend(parse_gazeta)
            print(f"📥 Получено {len(news)} новостей")

            if not news:
                print("⚠️ Новостей не найдено")
                return

            print(f"📥 Получено {len(news)} новостей")
            await save_news_to_db(news)
            print("✅ Новости сохранены")
        except Exception as e:
            print(f"💥 Ошибка в задаче: {e}")

def start_scheduler(loop: asyncio.AbstractEventLoop):
    print("🧪 start_scheduler вызван")
    scheduler = AsyncIOScheduler(event_loop=loop)

    def run_job():
        print("🧪 Запускаем scheduled_job")
        loop.call_soon_threadsafe(lambda: asyncio.create_task(scheduled_job()))

    scheduler.add_job(run_job, trigger="interval", minutes=10)
    scheduler.start()
    return scheduler
