.PHONY: help

.DEFAULT_GOAL := help
help:
	@echo "Доступные команды:"; \
	grep -E '^[a-zA-Z0-9_-]+:.*?## .+$$' $(MAKEFILE_LIST) | \
	awk -F':.*?## ' '{printf "  \033[36m%-20s\033[0m \033[33m%s\033[0m\n", $$1, $$2}'


install: ## Установить пакет зависимости с помощью uv + все dev-зависимости
	uv sync --all-extras

docker: ## Поднять PostgreSQL в Docker
	docker-compose up -d postgres
	sleep 3
	uv run python -m src.targeting_service.migrate

run: ## Запустить приложение локально
	uv run run

lint: ## Ruff: проверка кода
	uv run ruff check src

lint-fix: ## Ruff: проверка с автофиксами
	uv run ruff check src --fix

fmt: ## Ruff: форматирование кода
	uv run ruff format src

fmt-check: ## Ruff: проверка форматирования (без изменений)
	uv run ruff format src --check

lint-fmt: ## Ruff: Объединяющая 4 предыдущие команды операция
	uv run ruff check src
	uv run ruff check src --fix
	uv run ruff format src
	uv run ruff format src --check

test: ## Запуск тестирования кода
	PYTHONPATH=. uv run pytest