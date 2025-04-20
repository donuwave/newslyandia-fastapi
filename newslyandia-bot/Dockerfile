FROM mcr.microsoft.com/playwright/python:v1.51.0-jammy

# Рабочая папка внутри контейнера
WORKDIR /app

# Скопируем зависимости и установим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь код бота
COPY . .

# Команда запуска
CMD ["python", "main.py"]
