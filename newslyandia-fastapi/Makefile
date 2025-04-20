.DEFAULT_GOAL := help

HOST ?= localhost
PORT ?= 8001

run:
	uvicorn main:app --reload --env-file .local.env

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

