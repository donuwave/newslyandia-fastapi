.DEFAULT_GOAL := help

HOST ?= localhost
PORT ?= 8003

run_local:
	uvicorn main:app --reload --env-file .local.env --port ${PORT}

run_dev:
	uvicorn main:app --reload --env-file .dev.env
