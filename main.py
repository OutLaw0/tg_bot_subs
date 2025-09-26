# -*- coding: utf-8 -*-
"""
Главный файл для запуска Telegram-бота
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from aiohttp import web
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

            # Создаем aiohttp-приложение
            app = web.Application()

            # Регистратор апдейтов от Telegram
            async def handle_webhook(request: web.Request) -> web.Response:
                # Проверяем секрет при наличии
                if WEBHOOK_SECRET:
                    if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
                        return web.Response(status=403)

                data = await request.json()
                update = bot.session.json_loads(data)
                await dp.feed_update(bot, update)
                return web.Response(text="ok")

            app.router.add_post(WEBHOOK_PATH, handle_webhook)

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
