# Template Service

Сервис-шаблон для создания сервисов

## Стек

- **Python 3.12**
- **FastAPI** + uvicorn
- **uv** для управления зависимостями
- **Loguru** для логирования
- **Ruff** для линтинга/форматирования
- **Pytest** для тестов

## Требования

- Python 3.12
- [uv](https://github.com/astral-sh/uv) - менеджер пакетов

## Быстрый старт

```bash
# Установить зависимости
make install

# Скопировать и настроить .env
cp .env.example .env

# Запустить приложение
make run
```

Приложение будет доступно по адресу: http://localhost:8080

## Разработка

Все доступные команды описаны в [`Makefile`](Makefile):

```bash
make install     # Установка зависимостей
make run         # Запуск приложения
make lint-fmt    # Линтинг и форматирование
make test        # Запуск тестов
```

## Настройки

Переменные окружения описаны в [`.env.example`](.env.example).

## Docker

```bash
# Собрать образ
docker build -t targeting_service .

# Запустить контейнер
docker run -p 8080:8080 --env-file .env targeting_service
```

## Структура проекта

```
.
├── src/
│   ├── main.py                      # Точка входа FastAPI
│   └── service/
│       ├── config/                  # Настройки приложения
│       └── logging_config.py        # Настройка логирования
├── tests/                           # Тесты
├── Makefile                         # Команды для разработки
├── pyproject.toml                   # Зависимости и настройки проекта
└── Dockerfile                       # Docker образ
```

---

**BMK Team** © 2026
