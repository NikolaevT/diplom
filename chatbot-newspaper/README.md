# Chatbot NewsPaper - новостной Telegram бот

## Описание
Chatbot NewsPaper - новостной Telegram bot

## Установка
1. **Клонируйте репозиторий**
```bash
  git clone <ссылка_на_репозиторий>
  cd chatbot-newspaper/
```

2. **Создайте файл .env на основе env.example**

```bash
  cp env_example .env
```


#### Обязательные поля

- **MONGODB_URL** - URL для базы данных
  - Формат: `mongodb://ip_адрес: порт`
  - Пример: `mongodb://localhost:27017`

- **MONGODB_DATABASE** - Имя базы данных MongoDB
  - По умолчанию: `newspaper`
  - Имя базы данных для хранения чатов и сообщений

- **BOT_TOKEN** - Токен бота
- **CHAT_ID** - ID чата в Telegram

3. **Запустите скрипт сборки**
```bash
  ./build-chatbot-newspaper.sh
```

4. **Запустите Базу Данных через Docker Compose**
```bash
  docker compose up -d
```
