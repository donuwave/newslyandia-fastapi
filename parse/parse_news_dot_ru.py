from urllib.parse import urljoin
from playwright.async_api import async_playwright

async def parse_news_dot_ru():
    url = "https://news.ru"
    print("🌍 Начинаем парсинг news.ru")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=30000)
            await page.wait_for_selector('.center-importanrt__items', timeout=30000)

            news_items = await page.query_selector_all(".center-importanrt__item a")

            results = []

            for item in news_items:
                print("📄 Парсим новость")
                title = await item.inner_text()
                href = await item.get_attribute("href")
                full_url = href if href and href.startswith("http") else f"https://news.ru{href}"

                article_page = await browser.new_page()
                await article_page.goto(full_url, timeout=30000, wait_until="domcontentloaded")

                await article_page.wait_for_selector(".single-news__all-text", timeout=30000)
                content_div = await article_page.query_selector(".single-news__all-text")

                if content_div:
                    paragraphs = await content_div.query_selector_all("p")
                    content_parts = []
                    for p in paragraphs:
                        text = await p.inner_text()
                        if text.strip():
                            content_parts.append(text.strip())
                    content = "\n".join(content_parts)
                else:
                    content = "Контент не найден"

                image_block = await article_page.query_selector(".single-news__picture")
                img_tag = await image_block.query_selector("img") if image_block else None
                image_url = await img_tag.get_attribute("src") if img_tag else None
                image_url = urljoin(url, image_url) if image_url else None

                results.append({
                    "title": title,
                    "url": full_url,
                    "content": content,
                    "img": image_url
                })

            await browser.close()
            return results

    except Exception as e:
        return {"error": f"Ошибка при парсинге: {e}"}
