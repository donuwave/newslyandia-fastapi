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

    results = []

    # 1) Запускаем playwright
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
        except Exception as e:
            print(f"❌ Не удалось запустить браузер: {e}")
            return results

        page = await browser.new_page()

        # 2) Загружаем главную
        try:
            await safe_goto(page, base_url)
            await page.wait_for_selector('.w_col_wide', timeout=30000)
        except Exception as e:
            print(f"❌ Не удалось загрузить главную страницу: {e}")
            await browser.close()
            return results

        # 3) Собираем анонсы
        items = await page.query_selector_all('.w_col_wide')

        for item in items:
            try:
                print("📄 Парсим новость на главной")

                a = await item.query_selector("a")
                if not a:
                    continue

                href = await a.get_attribute("href") or ""
                full_url = href if href.startswith("http") else urljoin(base_url, href)

                # 4) Открываем статью
                article_page = await browser.new_page()
                await safe_goto(article_page, full_url)
                await article_page.wait_for_selector(".b_main", timeout=30000)

                # 5) Парсим заголовок
                h1 = await article_page.query_selector("h1")
                title = await h1.inner_text() if h1 else "Без заголовка"

                # 6) Парсим интро
                intro = await article_page.query_selector(".intro")
                content = await intro.inner_text() if intro else "Контент не найден"

                # 7) Парсим картинку
                img_el = await article_page.query_selector(".mainarea-wrapper img")
                raw_src = await img_el.get_attribute("src") if img_el else None
                img_url = urljoin(base_url, raw_src) if raw_src else None

                await article_page.close()

                results.append({
                    "title":   title.strip(),
                    "url":     full_url,
                    "content": content.strip(),
                    "img":     img_url
                })

            except Exception as e_item:
                print(f"⚠️ Ошибка при парсинге {full_url}: {e_item}")
                try:
                    await article_page.close()
                except:
                    pass
                continue

        await browser.close()

    return results
