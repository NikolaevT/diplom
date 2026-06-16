.PHONY: help install run docker docker-down up down mock-bmk mock-logs lint lint-fix fmt fmt-check test

.DEFAULT_GOAL := help

help: ## Показать это сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m \033[33m%s\033[0m\n", $$1, $$2}'

install: ## Установить зависимости с помощью uv
	uv sync --extra dev

run: ## Запустить приложение локально
	PYTHONPATH=bot uv run python -m src.main

docker: ## Поднять MongoDB (Docker)
	docker compose up -d

docker-down: ## Остановить MongoDB (Docker)
	docker compose down

up: ## Поднять Mock BMK-IT (Docker)
	docker compose -f docker-compose.mock.yml up -d --build

down: ## Остановить Mock BMK-IT (Docker)
	docker compose -f docker-compose.mock.yml down

mock-bmk: ## Запустить Mock BMK-IT локально (uvicorn)
	uv run uvicorn dev_tools.mock_bmk_it.main:app --reload --port 8088

mock-logs: ## Логи Mock BMK-IT (Docker)
	docker compose -f docker-compose.mock.yml logs -f mock-bmk-it

lint: ## Ruff: проверка кода
	uv run --extra dev ruff check bot/src dev_tools

lint-fix: ## Ruff: проверка с автофиксами
	uv run --extra dev ruff check bot/src dev_tools --fix

fmt: ## Ruff: форматирование кода
	uv run --extra dev ruff format bot/src dev_tools

fmt-check: ## Ruff: проверка форматирования (без изменений)
	uv run --extra dev ruff format bot/src dev_tools --check

test: ## Запустить pytest-тесты
	uv run --extra dev pytest
