#!/bin/sh

# Запуск Ollama API в фоне
ollama serve &

# Немного подождём, чтобы сервер успел подняться
sleep 2

# Прелоад нужной модели
curl -X POST http://localhost:11434/api/pull -d '{"name":"llama3:8b"}'

# Ждём завершения ollama (навсегда)
wait