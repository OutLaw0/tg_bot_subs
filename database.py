# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных PostgreSQL
"""

import asyncpg
import logging
from config import DATABASE_URL

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Класс для асинхронной работы с базой данных PostgreSQL"""

    def __init__(self, db_url: str = DATABASE_URL):
        """
        Инициализация пула соединений к базе данных.
        
        Args:
            db_url (str): URL для подключения к PostgreSQL
        """
        self.db_url = db_url
        self.pool = None

    async def connect(self):
        """Создание пула соединений и инициализация таблицы"""
        if not self.pool:
            try:
                self.pool = await asyncpg.create_pool(self.db_url)
                logger.info("Пул соединений к PostgreSQL создан успешно")
                await self.init_database()
            except Exception as e:
                logger.error(f"Ошибка при подключении к базе данных: {e}")

    async def init_database(self):
        """Создание таблицы пользователей, если она не существует"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                logger.info("Таблица 'users' инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка при инициализации таблицы: {e}")

    async def add_user(self, user_id: int, username: str = None, 
                       first_name: str = None, last_name: str = None) -> bool:
        """
        Добавление пользователя в базу данных.
        
        Returns:
            bool: True если пользователь добавлен, False если уже существует
        """
        try:
            async with self.pool.acquire() as conn:
                # INSERT ... ON CONFLICT DO NOTHING - безопасный способ добавить запись,
                # ничего не делая, если пользователь уже существует.
                result = await conn.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (user_id) DO NOTHING
                ''', user_id, username, first_name, last_name)
                
                # result в формате 'INSERT 0 1' означает, что 1 строка добавлена
                if result == 'INSERT 0 1':
                    logger.info(f"Пользователь {user_id} добавлен в базу данных")
                    return True
                else:
                    logger.info(f"Пользователь {user_id} уже существует")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False

    async def remove_user(self, user_id: int) -> bool:
        """
        Удаление пользователя из базы данных.
        
        Returns:
            bool: True если пользователь удален, False если не найден
        """
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("DELETE FROM users WHERE user_id = $1", user_id)
                # result в формате 'DELETE 1' означает, что 1 строка удалена
                if result == 'DELETE 1':
                    logger.info(f"Пользователь {user_id} удален из базы данных")
                    return True
                else:
                    logger.info(f"Пользователь {user_id} не найден в базе данных")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {e}")
            return False

    async def is_user_subscribed(self, user_id: int) -> bool:
        """Проверка подписки пользователя"""
        try:
            async with self.pool.acquire() as conn:
                user = await conn.fetchrow("SELECT user_id FROM users WHERE user_id = $1", user_id)
                return user is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки: {e}")
            return False

    async def get_all_users(self) -> list:
        """Получение списка ID всех подписанных пользователей"""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("SELECT user_id FROM users")
                return [row['user_id'] for row in rows]
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return []

    async def get_users_count(self) -> int:
        """Получение количества подписанных пользователей"""
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval("SELECT COUNT(*) FROM users")
                return count
        except Exception as e:
            logger.error(f"Ошибка при подсчете пользователей: {e}")
            return 0
            
    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Пул соединений к PostgreSQL закрыт")


# Создаем экземпляр базы данных
# Теперь подключение будет управляться в основном файле бота
db = Database()