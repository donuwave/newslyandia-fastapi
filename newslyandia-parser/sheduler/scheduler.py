import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import settings
from sheduler.add_new import add_news

job_lock = asyncio.Lock()

import asyncio
from playwright.async_api import async_playwright
import requests
import json
from bs4 import BeautifulSoup

OLLAMA_URL = settings.OLLAMA_URL
OLLAMA_MODEL = "llama3:8b"


async def extract_article_with_readability(page, url):
    readability_js = requests.get('https://cdn.jsdelivr.net/npm/@mozilla/readability@0.4.4/Readability.js').text
    await page.goto(url)
    await page.add_script_tag(content=readability_js)
    article = await page.evaluate("""
        () => {
            let article = new Readability(document).parse();
            return {
                title: article ? article.title : document.title,
                content: article ? article.textContent : '',
            };
        }
    """)
    return article['title'], article['content']

def extract_image(soup):
    img = soup.find("meta", property="og:image") or \
          soup.find("meta", property="twitter:image")
    if img and img.get("content"):
        return img["content"]
    img_tag = soup.find("img")
    return img_tag["src"] if img_tag and img_tag.get("src") else ""

async def parse_news_page(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        title, content = await extract_article_with_readability(page, url)
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        image = extract_image(soup)
        await browser.close()
        return title, content, image

def summarize(text):
    short_text = text[:3000]
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Ты — ассистент по подготовке новостных заметок."
                  f"Твоя задача: прочитать текст, выделить только главную новостную мысль и сформулировать её ровно в нескольких"
                  f"лаконичных, небольших предложениях в нейтральном новостном тоне. Никаких вводных фраз, оценок или комментариев — только фактическая суть."
                  f"На русском языке"
                  f":\n\n{short_text}\n\nОтвет:"
    }

    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    response_text = ""
    for line in response.iter_lines():
        if line:
            json_line = json.loads(line.decode('utf-8'))
            response_text += json_line.get("response", "")
    return response_text.strip()

async def is_article(page, url, word_threshold=150):
    try:
        title, content = await extract_article_with_readability(page, url)
        return len(content.split()) >= word_threshold
    except:
        return False

async def find_news_links(homepage_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(homepage_url)
        content = await page.content()
        soup = BeautifulSoup(content, "html.parser")

        links = {link["href"] for link in soup.find_all("a", href=True)}
        full_links = [requests.compat.urljoin(homepage_url, href) for href in links]
        domain = requests.utils.urlparse(homepage_url).netloc
        filtered_links = [link for link in full_links if requests.utils.urlparse(link).netloc == domain]

        print(f"Найдено {len(filtered_links)} ссылок, проверяем статьи...")

        for link in filtered_links:
            try:
                if await is_article(page, link):
                    print(f"[+] Статья: {link}")

                    title, full_text, image = await parse_news_page(link)
                    summary = summarize(full_text)
                    result = {
                        "url": link,
                        "title": title,
                        "text": summary,
                        "image": image
                    }

                    print(json.dumps(result, ensure_ascii=False, indent=4))

                    print('Сохраняем и отправляем запрос')
                    await add_news(result)

                else:
                    print(f"[-] Пропущено: {link}")
            except Exception as e:
                print(f"❌ Ошибка при обработке {link}: {e}")

        await browser.close()


async def scheduled_job():
    if job_lock.locked():
        print("⚠️ Предыдущая задача ещё работает, пропускаем запуск.")
        return

    async with job_lock:
        try:
            print(settings.NEWS_LINK)
            await find_news_links(settings.NEWS_LINK)
            print(f"Парсер закончил проходить по сайту news")
        except Exception as e:
            print(f"💥 Ошибка в задаче: {e}")


def start_scheduler(loop: asyncio.AbstractEventLoop):
    print("🧪 start_scheduler вызван")
    scheduler = AsyncIOScheduler(event_loop=loop)

    def run_job():
        print("🧪 Запускаем scheduled_job")
        loop.call_soon_threadsafe(lambda: asyncio.create_task(scheduled_job()))

    scheduler.add_job(run_job, trigger="interval", minutes=0.1)
    scheduler.start()
    return scheduler
