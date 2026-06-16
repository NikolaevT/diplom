# Mock Jira Service

Mock-сервис для имитации Jira Integration API при локальной разработке и записи демо (без доступа к реальному Jira).

## Возможности

- `GET /v1/project/by-telegramId/{telegram_id}` — список проектов (`availableProjects` в camelCase, как у боевого API).
- `POST /v1/issue/by-telegramId` — «создание» задачи, в ответе поле `issue` со ссылкой вида `http://127.0.0.1:8091/browse/TASK-N`.

Для любого `telegram_id`, которого нет в `test_data.MOCK_USERS`, возвращаются демо-проекты `DEFAULT_DEMO_PROJECTS` с **короткими URL** (чтобы inline-кнопки Telegram укладывались в лимит callback 64 байта).

## Запуск

Из корня репозитория:

```bash
make mock-jira
```

Или из этой папки:

```bash
uv run --with-requirements requirements.txt uvicorn main:app --reload --host 127.0.0.1 --port 8091
```

Swagger: http://127.0.0.1:8091/docs

## Подключение бота

В `.env` основного проекта:

```bash
JIRA_USE_MOCK=true
JIRA_MOCK_HOST=http://127.0.0.1:8091
```

Порт **8091** выбран сознательно: в `.env-example` у приложения часто `PORT=8080`, чтобы не было конфликта.

При `JIRA_USE_MOCK=true` бот **не требует** `AUTH_LOGIN` / `AUTH_PASSWORD` — для запросов к mock используется заглушка токена.

Сервис предназначен только для локальной разработки и не должен использоваться в продакшене.
