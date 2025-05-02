.DEFAULT_GOAL := help

HOST ?= localhost
PORT ?= 8000

run_local:
	uvicorn main:app --reload --env-file .local.env --port ${PORT}

run_dev:
	uvicorn main:app --reload --env-file .dev.env

install:
	@echo "Подтягиваем зависимость $(LIBRARY)"
	poetry add $(LIBRARY)

uninstall:
	@echo "Удаляем зависимость $(LIBRARY)"
	poetry remove $(LIBRARY)

migrate-create:
	alembic revision --autogenerate -m $(MESSAGE)

migrate-apply:
	alembic upgrade head

