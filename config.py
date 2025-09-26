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