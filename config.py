# -*- coding: utf-8 -*-
"""
Конфигурационный файл для Telegram-бота.
Значения читаются из переменных окружения.

Не храните реальные токены в репозитории.
"""

import os

# Автозагрузка .env при наличии python-dotenv (удобно локально и в Render Shell)
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass


def _get_admin_id() -> int:
    """Безопасно получить ADMIN_ID из окружения.

    Возвращает 0, если переменная не задана или не является числом.
    """
    value = os.getenv("ADMIN_ID", "0").strip()
    try:
        return int(value)
    except Exception:
        return 0


# Токен бота (обязательно)
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# ID администратора (целое число, по умолчанию 0 — нет прав админа)
ADMIN_ID = _get_admin_id()

# Название файла базы данных (SQLite)
DATABASE_NAME = os.getenv("DATABASE_NAME", "bot_users.db").strip() or "bot_users.db"

# Порт для веб-сервера (Render/Heroku предоставляет переменную PORT)
PORT = int(os.getenv("PORT", "8000"))

# Базовый публичный URL приложения для вебхука.
# На Render доступна переменная RENDER_EXTERNAL_URL, можно переопределить через WEBHOOK_BASE_URL
WEBHOOK_BASE_URL = (
    os.getenv("WEBHOOK_BASE_URL")
    or os.getenv("RENDER_EXTERNAL_URL", "").rstrip("/")
)

# Путь вебхука, например /webhook
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook").strip() or "/webhook"

# Секрет вебхука (опционально). Если задан, Telegram будет отправлять заголовок X-Telegram-Bot-Api-Secret-Token
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")