# Chatbot Task Manager

Telegram-бот для управления задачами с интеграцией Jira.

## Быстрый старт

1. Посмотреть доступные команды через make

2. переменные окружения
```
# Токен Telegram бота
# Получите токен у @BotFather в Telegram
BOT_TOKEN=your_bot_token_here

# Окружение: development (локально) или production/staging (на стенде)
ENVIRONMENT=development

# MongoDB настройки
MONGODB_URL=mongodb://localhost:27017
MONGODB_NAME=task_manager
MONGODB_COLLECTION=chats

# MongoDB аутентификация (опционально для development, ОБЯЗАТЕЛЬНО для production/staging)
MONGODB_USERNAME=your_username
MONGODB_PASSWORD=your_password
MONGODB_AUTH_SOURCE=admin  # Обычно 'admin', можно не указывать

# Параметры polling (опционально)
POLLING_TIMEOUT=30              # Таймаут long polling в секундах (по умолчанию: 30)
POLLING_REQUEST_TIMEOUT=30      # Таймаут запросов к API в секундах (по умолчанию: 30)
POLLING_CLOSE_TIMEOUT=10        # Таймаут закрытия соединения в секундах (по умолчанию: 10)
POLLING_ALLOWED_UPDATES=message,callback_query  # Типы обновлений через запятую (по умолчанию: все)

# Интеграция с внешним сервисом Jira
JIRA_HOST=https://your-jira-service.example.com

# Локальная демо без реального Jira (см. раздел ниже)
JIRA_USE_MOCK=true
JIRA_MOCK_HOST=http://127.0.0.1:8091

# LLM — корпоративный vLLM
VLLM_BASE_URL=http://10.45.0.75:8000/v1
VLLM_API_KEY=not-needed
LLM_MODEL_NAME=Qwen/Qwen3.6-35B-A3B-FP8
LLM_TEMPERATURE=0.7
LLM_REASONING=false
LLM_MAX_TOKENS=5000
AGENT_REQUEST_LIMIT=30
AGENT_TOOL_CALLS_LIMIT=10
```

## Разработка

### Локальная разработка с Mock Jira Service

Для тестирования бота без подключения к реальному Jira используй mock-сервис на FastAPI, расположенный в `dev_tools/mock_jira_service/`.

Запуск mock-сервиса:
```bash
make mock-jira
```

В `.env` основного приложения включи режим mock (отдельный URL, чтобы не трогать `JIRA_HOST` продакшена):
```bash
JIRA_USE_MOCK=true
JIRA_MOCK_HOST=http://127.0.0.1:8091
```

Mock слушает **8091**, чтобы не пересекаться с типичным `PORT=8080` бота/API.

Инфо: [dev_tools/mock_jira_service/README.md](dev_tools/mock_jira_service/README.md)
