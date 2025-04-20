FROM python:3.10-slim

# Рабочая папка внутри контейнера
WORKDIR /app

# Скопируем зависимости и установим их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Скопируем весь код бота
COPY . .

# Команда запуска
CMD ["python", "main.py"]
