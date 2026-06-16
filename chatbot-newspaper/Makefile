.PHONY: help

.DEFAULT_GOAL := help
help:
	@echo "Доступные команды:"; \
	grep -E '^[a-zA-Z0-9_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
	awk -F':.*?## ' '{printf "  \033[36m%-20s\033[0m \033[33m%s\033[0m\n", $$1, $$2}'


install: ## Установить зависимости с помощью uv
	uv sync

up: ## Запустить приложение в Docker
	docker-compose up -d
down: ## Остановить приложение в Docker
	docker-compose down

run: ## Запустить приложение локально
	uv run run

lint: ## Ruff: проверка кода
	uv run --extra dev ruff check src

lint-fix: ## Ruff: проверка с автофиксами
	uv run --extra dev ruff check src --fix

fmt: ## Ruff: форматирование кода
	uv run --extra dev ruff format src

fmt-check: ## Ruff: проверка форматирования (без изменений)
	uv run --extra dev ruff format src --check