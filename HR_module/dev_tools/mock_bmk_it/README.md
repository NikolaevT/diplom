# Mock BMK-IT Service

Локальная имитация **БМК-ИТ** для разработки HR middleware без реального стенда.

## Эндпоинты (вызовы от middleware)

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/candidates` | Регистрация кандидата после `/start` в боте |
| `GET` | `/candidates/{telegram_id}` | Проверка, что кандидат уже зарегистрирован |
| `POST` | `/appointments` | HR назначает собеседование → вызов middleware |
| `POST` | `/offers` | HR отправляет оффер (multipart: файл + offerId, telegramId) |
| `GET` | `/offers/{offer_id}/file` | Скачать файл оффера |
| `POST` | `/instructions` | HR отправляет инструкцию (multipart: файл + instructionId, telegramId) |
| `GET` | `/instructions/{instruction_id}/file` | Скачать файл инструкции |
| `PUT` | `/appointment/confirm` | Кандидат согласился на собеседование |
| `POST` | `/appointment/reschedule` | Кандидат запросил перенос |
| `DELETE` | `/appointment` | Кандидат отказался (query: `appointmentId`, `telegramId`) |
| `PUT` | `/offer/accept` | Кандидат принял оффер |
| `PUT` | `/offer/reject` | Кандидат отклонил оффер |

Уведомления HR имитируются выводом в консоль: `[MOCK BMK-IT → HR] ...`

## Запуск

**Полный локальный стек:**

```bash
make install
make docker        # MongoDB на :27017
make up            # Mock BMK-IT в Docker на :8088
make run           # бот (FastAPI + polling), нужен .env в корне репозитория
```

**Только Mock BMK-IT (Docker):**

```bash
make install
make up            # поднять
make down          # остановить
make mock-logs     # логи
make test          # pytest
```

Swagger: http://localhost:8088/docs

**Локально без Docker (mock):**

```bash
make install
make mock-bmk
```

## Отладка

- `GET /debug/candidates` — список зарегистрированных кандидатов
- `GET /debug/appointments` — список назначенных собеседований
- `GET /debug/offers` — список отправленных офферов
- `GET /debug/instructions` — список отправленных инструкций
- `GET /debug/notifications` — список «уведомлений HR»
- `DELETE /debug/notifications` — очистить список

Только для разработки.
