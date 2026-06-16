.PHONY: help install run test lint lint-fix fmt fmt-check

.DEFAULT_GOAL := help

help: ## Показать это сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m \033[33m%s\033[0m\n", $$1, $$2}'

install: ## Установить зависимости с помощью uv
	uv sync

run: ## Запустить приложение локально
	uv run python -m src.main

test: ## Запустить тесты
	uv run --extra dev pytest tests -v

lint: ## Ruff: проверка кода
	uv run --extra dev ruff check src tests

lint-fix: ## Ruff: проверка с автофиксами
	uv run --extra dev ruff check src tests --fix

fmt: ## Ruff: форматирование кода
	uv run --extra dev ruff format src tests

fmt-check: ## Ruff: проверка форматирования (без изменений)
	uv run --extra dev ruff format src tests --check
