from urllib.parse import urljoin
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

async def safe_goto(page, url, timeout=30000):
    try:
        return await page.goto(url, timeout=timeout, wait_until="networkidle")
    except PlaywrightTimeoutError:
        return await page.goto(url, timeout=timeout, wait_until="domcontentloaded")

async def parse_news_gazeta():
    base_url = "https://www.gazeta.ru"
    print("🌍 Начинаем парсинг gazeta.ru")

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # 1) Главная страница
            await safe_goto(page, base_url)
            await page.wait_for_selector('.w_col_wide', timeout=30000)
            news_items = await page.query_selector_all('.w_col_wide')

            results = []

            for item in news_items:
                print("📄 Парсим новость на главной")
                a = await item.query_selector("a")
                if not a:
                    continue

                href = await a.get_attribute("href") or ""
                full_url = href if href.startswith("http") else urljoin(base_url, href)

                # 2) Открываем статью
                article_page = await browser.new_page()
                await safe_goto(article_page, full_url)
                await article_page.wait_for_selector(".b_main", timeout=30000)

                # 3) Заголовок
                title_block = await article_page.query_selector("h1")
                title = await title_block.inner_text() if title_block else "Без заголовка"

                # 4) Интро/анонс
                content_block = await article_page.query_selector(".intro")
                content = await content_block.inner_text() if content_block else "Контент не найден"

                # 5) Картинка
                img_el = await article_page.query_selector(".mainarea-wrapper img")
                raw_src = await img_el.get_attribute("src") if img_el else None
                image_url = urljoin(base_url, raw_src) if raw_src else None

                await article_page.close()

                results.append({
                    "title": title.strip(),
                    "url": full_url,
                    "content": content.strip(),
                    "img": image_url
                })

            await browser.close()
            return results

    except Exception as e:
        return {"error": f"Ошибка при парсинге: {e}"}
