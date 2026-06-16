.PHONY: help install run mongo mock-jira

.DEFAULT_GOAL := help
# Помощь по доступным командам
help: ## Показать это сообщение
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m \033[33m%s\033[0m\n", $$1, $$2}'

install: ## Установить зависимости с помощью uv
	uv sync

run: ## Запустить приложение локально
	uv run python -m src.main

docker: ## Поднять MongoDB базу данных и Chromadb
	docker-compose up -d

mock-jira: ## Запустить Mock Jira Service для разработки (порт 8091, не конфликтует с ботом на 8080)
	@cd dev_tools/mock_jira_service && \
	uv run --with-requirements requirements.txt uvicorn main:app --reload --host 127.0.0.1 --port 8091

lint: ## Ruff: проверка кода
	uv run --extra dev ruff check src

lint-fix: ## Ruff: проверка с автофиксами
	uv run --extra dev ruff check src --fix

fmt: ## Ruff: форматирование кода
	uv run --extra dev ruff format src

fmt-check: ## Ruff: проверка форматирования (без изменений)
	uv run --extra dev ruff format src --check