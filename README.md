# 📰 Newslyandia

Автоматический новостной Telegram-канал. Парсеры собирают свежие статьи с новостных сайтов, локальная LLM (Llama 3 через Ollama) пересказывает каждую в несколько предложений, а админы канала просматривают, редактируют и публикуют новости прямо из Telegram-бота. Там же бот проводит розыгрыши среди комментаторов.

![Статус](https://img.shields.io/badge/статус-в_разработке-orange?style=flat)

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat&logo=postgresql&logoColor=white)
![Telegram](https://img.shields.io/badge/Telethon-26A5E4?style=flat&logo=telegram&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=flat&logo=playwright&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama_·_Llama_3-000000?style=flat&logo=ollama&logoColor=white)
![Docker](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat&logo=docker&logoColor=white)

## Как это работает

```mermaid
flowchart LR
    S1[news.ru] --> P1[parser_1]
    S2[vesti.ru] --> P2[parser_2]
    P1 -- текст статьи --> LLM[Ollama<br/>Llama 3 8B]
    P2 -- текст статьи --> LLM
    LLM -- краткий пересказ --> P1
    LLM -- краткий пересказ --> P2
    P1 -- POST /news --> API[FastAPI + PostgreSQL]
    P2 -- POST /news --> API
    API <--> BOT[Telegram-бот]
    ADM((Админы канала)) <--> BOT
    BOT -- публикация --> CH[Канал @newslyandia]
    CH --> GR[Группа обсуждения]
    GR -- комментарии --> BOT
```

1. **Парсер** по расписанию открывает главную страницу сайта в headless-браузере, собирает ссылки своего домена и для каждой проверяет, статья ли это (Mozilla Readability, порог по количеству слов).
2. Из статьи извлекаются заголовок, текст и обложка (`og:image`).
3. Текст уходит в **локальную LLM** с промптом: выделить главную новость и пересказать её в нескольких предложениях в нейтральном тоне.
4. Результат сохраняется через **API** в Postgres. Повторная статья отсекается по уникальному URL.
5. Админ пишет боту `/news` и получает список новостей: превью, полный текст, правка, публикация в канал с подписью-призывом.
6. **Розыгрыши:** `/create_giveaway` публикует конкурсный пост, бот собирает комментаторов из группы обсуждения, `/select_winner` выбирает победителя.

## Сервисы

| Сервис | Что делает | Стек |
| --- | --- | --- |
| [`newslyandia-parser`](newslyandia-parser) | Поиск и разбор статей, пересказ через LLM, отправка в API. Один образ запускается несколько раз — по контейнеру на источник (`NEWS_LINK`) | FastAPI (lifespan), APScheduler, Playwright, BeautifulSoup, Readability.js |
| [`newslyandia-model`](newslyandia-model) | Локальная LLM, при старте подтягивает модель | Ollama, Llama 3 8B |
| [`newslyandia-fastapi`](newslyandia-fastapi) | Хранение новостей и розыгрышей, REST API | FastAPI, SQLAlchemy, Alembic, PostgreSQL |
| [`newslyandia-bot`](newslyandia-bot) | Модерация и публикация новостей, розыгрыши. Доступ только у админов канала | Telethon, httpx |

## Технические детали

- **Микросервисы в одном Docker Compose**: БД, API, бот, два парсера и LLM, общение по HTTP внутри сети compose
- **Горизонтальное масштабирование парсеров**: новый источник — это новый контейнер того же образа с другой переменной `NEWS_LINK`
- **Защита от наложения задач**: `asyncio.Lock` пропускает запуск, если предыдущий проход по сайту ещё не закончился
- **Локальная LLM без внешних API**: Ollama на CPU с ограничением ресурсов контейнера (`cpus`, `mem_limit`)
- **Извлечение статей «как в Firefox»**: Readability.js внедряется в страницу Playwright, поэтому не нужно писать отдельный парсер под вёрстку каждого сайта
- **Мягкое удаление новостей** через поле `deleted_at`
- **API разбит на слои**: `handler` → `service` → `repository`, зависимости через `Depends`
- **Доступ к боту** ограничен списком админов канала на уровне фильтров событий Telethon

## Запуск

Нужны Docker и Docker Compose. Модель весит около 5 ГБ и при первом запуске скачивается автоматически.

1. Создай Telegram-бота у [@BotFather](https://t.me/BotFather), получи `API_ID` и `API_HASH` на [my.telegram.org](https://my.telegram.org), добавь бота админом в канал и группу обсуждения.
2. Создай `.dev.env` в каждом сервисе по примеру `.env.example`.
3. Подними всё:

```bash
docker compose -f docker-compose.dev.yml up -d --build
make alembic_dev_upgrade_app   # миграции
```

4. Напиши боту `/news`.

| Сервис | Порт |
| --- | --- |
| API (Swagger: `/docs`) | 8000 |
| Бот | 8001 |
| Парсеры | 8003, 8004 |
| Ollama | 11434 |
| PostgreSQL | 5432 |
