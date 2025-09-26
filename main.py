# -*- coding: utf-8 -*-
"""
Главный файл для запуска Telegram-бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска бота
    """
    bot = None
    try:
        # Проверяем наличие токена
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не задан. Укажите токен в переменной окружения или .env")
            return
        
        # Создаем экземпляры бота и диспетчера
        bot = Bot(token=BOT_TOKEN)
        dp = Dispatcher(storage=MemoryStorage())
        
        # Подключаем роутер с обработчиками
        dp.include_router(router)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот запущен: @{bot_info.username} ({bot_info.first_name})")
        
        # Запускаем бота
        logger.info("🚀 Бот готов к работе...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        # Закрываем сессию бота, если он был создан
        if bot is not None:
            await bot.session.close()


if __name__ == '__main__':
    try:
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
