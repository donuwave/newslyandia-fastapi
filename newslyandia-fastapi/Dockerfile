FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# чтобы pip выводил сразу в консоль
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# сначала только зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# копируем весь код (исключите .env-файлы через .dockerignore, если хотите)
COPY . .

ENTRYPOINT []

EXPOSE 8000

RUN ln -s /app /app/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--env-file", ".dev.env"]
