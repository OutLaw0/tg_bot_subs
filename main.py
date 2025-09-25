# -*- coding: utf-8 -*-
"""
Главный файл для запуска Telegram-бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import (
    start_command,
    unsubscribe_command,
    send_command,
    stats_command,
    help_command,
    handle_unknown_message
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def register_handlers(dp: Dispatcher):
    """
    Регистрация обработчиков команд
    
    Args:
        dp (Dispatcher): Диспетчер aiogram
    """
    # Регистрируем обработчики команд
    dp.register_message_handler(start_command, commands=['start'])
    dp.register_message_handler(unsubscribe_command, commands=['unsubscribe'])
    dp.register_message_handler(send_command, commands=['send'])
    dp.register_message_handler(stats_command, commands=['stats'])
    dp.register_message_handler(help_command, commands=['help'])
    
    # Обработчик для всех остальных сообщений
    dp.register_message_handler(handle_unknown_message, content_types=['text'])


async def main():
    """
    Основная функция запуска бота
    """
    try:
        # Проверяем наличие токена
        if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            logger.error("❌ Токен бота не установлен! Укажите токен в config.py")
            return
        
        # Создаем экземпляры бота и диспетчера
        bot = Bot(token=BOT_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(bot, storage=storage)
        
        # Регистрируем обработчики
        await register_handlers(dp)
        
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"🤖 Бот запущен: @{bot_info.username} ({bot_info.first_name})")
        
        # Запускаем бота
        logger.info("🚀 Бот готов к работе...")
        await dp.start_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
    finally:
        # Закрываем сессию бота
        await bot.session.close()


if __name__ == '__main__':
    try:
        # Запускаем бота
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
