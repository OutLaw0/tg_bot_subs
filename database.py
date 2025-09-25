# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных SQLite
"""

import sqlite3
import logging
from config import DATABASE_NAME

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Database:
    """Класс для работы с базой данных пользователей"""
    
    def __init__(self, db_name: str = DATABASE_NAME):
        """
        Инициализация подключения к базе данных
        
        Args:
            db_name (str): Название файла базы данных
        """
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Создание таблицы пользователей, если она не существует"""
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
                logger.info("База данных инициализирована успешно")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
    
    def add_user(self, user_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None) -> bool:
        """
        Добавление пользователя в базу данных
        
        Args:
            user_id (int): ID пользователя в Telegram
            username (str): Имя пользователя (@username)
            first_name (str): Имя пользователя
            last_name (str): Фамилия пользователя
            
        Returns:
            bool: True если пользователь добавлен, False если уже существует
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                
                # Проверяем, существует ли пользователь
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                if cursor.fetchone():
                    return False  # Пользователь уже существует
                
                # Добавляем нового пользователя
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                logger.info(f"Пользователь {user_id} добавлен в базу данных")
                return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении пользователя: {e}")
            return False
    
    def remove_user(self, user_id: int) -> bool:
        """
        Удаление пользователя из базы данных
        
        Args:
            user_id (int): ID пользователя в Telegram
            
        Returns:
            bool: True если пользователь удален, False если не найден
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Пользователь {user_id} удален из базы данных")
                    return True
                else:
                    logger.info(f"Пользователь {user_id} не найден в базе данных")
                    return False
        except Exception as e:
            logger.error(f"Ошибка при удалении пользователя: {e}")
            return False
    
    def is_user_subscribed(self, user_id: int) -> bool:
        """
        Проверка подписки пользователя
        
        Args:
            user_id (int): ID пользователя в Telegram
            
        Returns:
            bool: True если пользователь подписан, False если нет
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
                return cursor.fetchone() is not None
        except Exception as e:
            logger.error(f"Ошибка при проверке подписки: {e}")
            return False
    
    def get_all_users(self) -> list:
        """
        Получение списка всех подписанных пользователей
        
        Returns:
            list: Список кортежей с данными пользователей
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users")
                return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Ошибка при получении списка пользователей: {e}")
            return []
    
    def get_users_count(self) -> int:
        """
        Получение количества подписанных пользователей
        
        Returns:
            int: Количество пользователей
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM users")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Ошибка при подсчете пользователей: {e}")
            return 0


# Создаем экземпляр базы данных
db = Database()

