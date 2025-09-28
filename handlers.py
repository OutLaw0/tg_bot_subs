# -*- coding: utf-8 -*-
"""
Обработчики команд для Telegram-бота
"""

import logging
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

from config import ADMIN_ID
from database import db  # db теперь асинхронный

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем роутер
router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    """
    Обработчик команды /start
    Регистрирует пользователя в базе данных
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    try:
        # Проверяем, подписан ли пользователь
        if await db.is_user_subscribed(user_id):
            await message.answer(
                "✅ Вы уже подписаны на рассылку!\n\n"
                "Используйте /unsubscribe для отписки."
            )
        else:
            # Добавляем пользователя в базу данных
            if await db.add_user(user_id, username, first_name, last_name):
                await message.answer(
                    "🎉 Добро пожаловать!\n\n"
                    "Вы успешно подписались на рассылку.\n"
                    "Используйте /unsubscribe для отписки.\n"
                    "/help - чтобы посмотреть прочие комманды"
                )
                logger.info(f"Новый пользователь {user_id} подписался")
            else:
                await message.answer(
                    "❌ Произошла ошибка при подписке.\n"
                    "Попробуйте позже."
                )
    except Exception as e:
        logger.error(f"Ошибка в start_command: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже."
        )


@router.message(Command("unsubscribe"))
async def unsubscribe_command(message: Message):
    """
    Обработчик команды /unsubscribe
    Удаляет пользователя из базы данных
    """
    user_id = message.from_user.id
    
    try:
        if await db.remove_user(user_id):
            await message.answer(
                "👋 Вы отписались от рассылки.\n\n"
                "Используйте /start для повторной подписки."
            )
            logger.info(f"Пользователь {user_id} отписался")
        else:
            await message.answer(
                "ℹ️ Вы не были подписаны на рассылку.\n\n"
                "Используйте /start для подписки."
            )
    except Exception as e:
        logger.error(f"Ошибка в unsubscribe_command: {e}")
        await message.answer(
            "❌ Произошла ошибка. Попробуйте позже."
        )


@router.message(Command("send"))
async def send_command(message: Message):
    """
    Обработчик команды /send
    Отправляет сообщение всем подписанным пользователям
    Доступно только администратору
    """
    # Проверяем права администратора
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    # Извлекаем текст сообщения
    if not message.text or len(message.text.split()) < 2:
        await message.answer(
            "📝 Использование: /send <текст сообщения>\n\n"
            "Пример: /send Привет всем! Это тестовая рассылка."
        )
        return
    
    message_text = message.text.split(' ', 1)[1]
    
    try:
        # Получаем список всех пользователей
        users = await db.get_all_users()
        if not users:
            await message.answer("📭 Нет подписанных пользователей для рассылки.")
            return
        
        # Отправляем сообщение каждому пользователю
        successful_sends = 0
        failed_sends = 0
        total_users = len(users)
        
        await message.answer(f"📤 Начинаю рассылку для {total_users} пользователей...")
        
        for user_id_to_send in users:
            try:
                await message.bot.send_message(user_id_to_send, message_text)
                successful_sends += 1
            except TelegramBadRequest as e:
                # Пользователь заблокировал бота или чат не найден
                failed_sends += 1
                logger.warning(f"Не удалось отправить сообщение пользователю {user_id_to_send}: {e}")
            except Exception as e:
                failed_sends += 1
                logger.error(f"Ошибка при отправке сообщения пользователю {user_id_to_send}: {e}")
        
        # Отправляем отчет администратору
        report = (
            f"📊 Рассылка завершена!\n\n"
            f"✅ Успешно отправлено: {successful_sends}\n"
            f"❌ Не удалось отправить: {failed_sends}\n"
            f"📝 Всего пользователей: {total_users}"
        )
        
        await message.answer(report)
        logger.info(f"Рассылка завершена: {successful_sends} успешно, {failed_sends} ошибок")
        
    except Exception as e:
        logger.error(f"Ошибка в send_command: {e}")
        await message.answer(
            "❌ Произошла ошибка при рассылке. Попробуйте позже."
        )


@router.message(Command("stats"))
async def stats_command(message: Message):
    """
    Обработчик команды /stats
    Показывает статистику подписок
    Доступно только администратору
    """
    # Проверяем права администратора
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ У вас нет прав для выполнения этой команды.")
        return
    
    try:
        users_count = await db.get_users_count()
        await message.answer(
            f"📊 Статистика бота:\n\n"
            f"👥 Всего подписчиков: {users_count}"
        )
    except Exception as e:
        logger.error(f"Ошибка в stats_command: {e}")
        await message.answer(
            "❌ Произошла ошибка при получении статистики."
        )


# Команды /help и обработчик неизвестных команд остаются без изменений,
# так как они не взаимодействуют с базой данных.
@router.message(Command("help"))
async def help_command(message: Message):
    """
    Обработчик команды /help
    Показывает список доступных команд
    """
    is_admin = message.from_user.id == ADMIN_ID
    
    help_text = (
        "🤖 Список команд:\n\n"
        "👋 /start - Подписаться на рассылку\n"
        "🚫 /unsubscribe - Отписаться от рассылки\n"
        "❓ /help - Показать эту справку"
    )
    
    if is_admin:
        help_text += (
            "\n\n🔧 Команды администратора:\n"
            "📤 /send <текст> - Отправить рассылку всем подписчикам\n"
            "📊 /stats - Показать статистику подписок"
        )
    
    await message.answer(help_text)


@router.message()
async def handle_unknown_message(message: Message):
    """
    Обработчик неизвестных сообщений
    """
    await message.answer(
        "❓ Неизвестная команда.\n\n"
        "Используйте /help для просмотра доступных команд."
    )