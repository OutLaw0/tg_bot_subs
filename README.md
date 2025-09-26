# Telegram Bot для рассылки

Telegram-бот на Python с использованием aiogram для управления подписками и рассылки сообщений.

## Функционал

### Для пользователей:
- `/start` - Подписаться на рассылку
- `/unsubscribe` - Отписаться от рассылки  
- `/help` - Справка по командам

### Для администратора:
- `/send <текст>` - Отправить рассылку всем подписчикам
- `/stats` - Показать статистику подписок

## Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Настройка конфигурации
Создайте файл `.env`:
```env
BOT_TOKEN=ВАШ_ТОКЕН_БОТА
ADMIN_ID=ВАШ_TELEGRAM_ID
DATABASE_NAME=bot_users.db
```

**Как получить токен бота:**
1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Скопируйте полученный токен

**Как узнать свой Telegram ID:**
1. Напишите @userinfobot в Telegram
2. Он пришлет ваш ID

### 3. Запуск бота

**Локально (polling):**
```bash
python main.py
```

**С webhook (для тестирования):**
```bash
# Добавьте в .env
echo WEBHOOK_BASE_URL=https://your-tunnel-url.ngrok.io >> .env
python main.py
```

## Деплой на Render

1. Создайте Web Service на Render и подключите репозиторий
2. В Settings → Environment добавьте:
   - `BOT_TOKEN` — токен бота
   - `ADMIN_ID` — ваш Telegram ID
   - `WEBHOOK_SECRET` — опционально (строка для проверки)
3. Стартовая команда: `python main.py`
4. Health check: `https://your-app.onrender.com/`

## Структура проекта

```
tg_bot_subs/
├── main.py          # Запуск бота
├── database.py      # Работа с SQLite
├── config.py        # Конфигурация
├── handlers.py      # Обработчики команд
├── requirements.txt # Зависимости
└── README.md        # Документация
```

## Особенности

- ✅ Автоматическое создание базы данных
- ✅ Обработка ошибок при рассылке
- ✅ Логирование операций
- ✅ Проверка прав администратора
- ✅ Поддержка polling и webhook режимов
- ✅ FastAPI для высокой производительности