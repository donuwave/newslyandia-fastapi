FROM python:3.10-slim

WORKDIR /app

# Установим системные зависимости для playwright
RUN apt-get update && \
    apt-get install -y wget gnupg curl libglib2.0-0 libnss3 libgconf-2-4 libfontconfig1 libxss1 libasound2 libxtst6 libx11-xcb1 libxcb1 libxcomposite1 libxdamage1 libxrandr2 libgtk-3-0 libgbm1 && \
    apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Установка браузеров для playwright
RUN playwright install --with-deps

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "--env-file", ".dev.env"]