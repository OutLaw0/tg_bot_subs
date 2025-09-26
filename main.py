# -*- coding: utf-8 -*-
"""
Главный файл для запуска Telegram-бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from config import BOT_TOKEN, PORT, WEBHOOK_BASE_URL, WEBHOOK_PATH, WEBHOOK_SECRET
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
        
        # Если задан WEBHOOK_BASE_URL — запускаем webhook-сервер, иначе polling
        if WEBHOOK_BASE_URL:
            # Настраиваем webhook
            webhook_url = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"
            await bot.set_webhook(
                url=webhook_url,
                secret_token=WEBHOOK_SECRET or None,
            )
            logger.info(f"🔗 Webhook установлен: {webhook_url}")

            # Создаем aiohttp-приложение и регистрируем обработчик aiogram
            app = web.Application()
            request_handler = SimpleRequestHandler(
                dispatcher=dp,
                bot=bot,
                secret_token=WEBHOOK_SECRET or None,
            )
            request_handler.register(app, path=WEBHOOK_PATH)
            setup_application(app, dp, bot=bot)

            # health-check endpoint для Render
            async def health(_: web.Request) -> web.Response:
                return web.Response(text="ok")

            app.router.add_get("/", health)

            logger.info(f"🛰️ Слушаю порт {PORT} для вебхуков...")
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, host="0.0.0.0", port=PORT)
            await site.start()

            # Ждем бесконечно, пока процесс работает
            while True:
                await asyncio.sleep(3600)
        else:
            logger.info("📡 WEBHOOK_BASE_URL не задан — запускаю polling (локальный режим)")
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
