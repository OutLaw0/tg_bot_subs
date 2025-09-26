# -*- coding: utf-8 -*-
"""
Telegram Bot для рассылки сообщений
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request, HTTPException
from config import BOT_TOKEN, PORT, WEBHOOK_BASE_URL, WEBHOOK_PATH, WEBHOOK_SECRET
from handlers import router

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Глобальные переменные
bot = None
dp = None

async def init_bot():
    """Инициализация бота"""
    global bot, dp
    
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN не задан. Укажите токен в переменной окружения или .env")
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    
    bot_info = await bot.get_me()
    logger.info(f"🤖 Бот запущен: @{bot_info.username} ({bot_info.first_name})")
    
    return bot, dp

async def setup_webhook():
    """Настройка webhook"""
    if not WEBHOOK_BASE_URL:
        raise ValueError("❌ WEBHOOK_BASE_URL не задан. Укажите публичный URL сервиса")
    
    webhook_url = f"{WEBHOOK_BASE_URL}{WEBHOOK_PATH}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=WEBHOOK_SECRET or None,
    )
    logger.info(f"🔗 Webhook установлен: {webhook_url}")

# FastAPI приложение
app = FastAPI(title="Telegram Bot")

@app.get("/")
async def health():
    """Health check endpoint для Render"""
    return {"status": "ok", "message": "Bot is running"}

@app.post(WEBHOOK_PATH)
async def webhook(request: Request):
    if not bot or not dp:
        raise HTTPException(status_code=503, detail="Bot not ready")
    
    # Проверка секрета
    if WEBHOOK_SECRET:
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") != WEBHOOK_SECRET:
            raise HTTPException(status_code=403)
    
    # Обработка обновления
    data = await request.json()
    from aiogram.types import Update
    update = Update.model_validate(data, from_attributes=True)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.on_event("startup")
async def startup():
    try:
        await init_bot()
        if WEBHOOK_BASE_URL:
            await setup_webhook()
            logger.info(f"Сервер запущен на порту {PORT}")
        else:
            asyncio.create_task(dp.start_polling(bot))
            logger.info("Запущен polling режим")
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации бота: {e}")

@app.on_event("shutdown")
async def shutdown():
    if bot:
        await bot.session.close()

if __name__ == '__main__':
    import uvicorn
    
    try:
        if WEBHOOK_BASE_URL:
            uvicorn.run("main:app", host="0.0.0.0", port=PORT)
        else:
            asyncio.run(init_bot())
            asyncio.run(dp.start_polling(bot))
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Ошибка: {e}")