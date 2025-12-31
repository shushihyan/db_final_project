#!/usr/bin/env python3
"""
Скрипт инициализации базы данных.
Создает базу, пользователя и таблицы.
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Создает базу данных и пользователя"""
    
    # Параметры подключения к PostgreSQL
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    admin_user = os.getenv("DB_ADMIN_USER", "postgres")
    admin_password = os.getenv("DB_ADMIN_PASSWORD", "password")
    
    # Параметры для новой БД
    db_name = os.getenv("DB_NAME", "library_db")
    db_user = os.getenv("DB_USER", "library_user")
    db_password = os.getenv("DB_PASSWORD", "library_password")
    
    try:
        # Подключаемся к PostgreSQL как администратор
        print(f"Подключение к PostgreSQL как {admin_user}...")
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=admin_user,
            password=admin_password
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Создаем пользователя (если не существует)
        print(f"Создание пользователя {db_user}...")
        cursor.execute(f"SELECT 1 FROM pg_roles WHERE rolname = '{db_user}'")
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE USER {db_user} 
                WITH PASSWORD '{db_password}' 
                CREATEDB
            """)
            print(f"Пользователь {db_user} создан")
        else:
            print(f"Пользователь {db_user} уже существует")
        
        # Создаем базу данных (если не существует)
        print(f"Создание базы данных {db_name}...")
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        if not cursor.fetchone():
            cursor.execute(f"""
                CREATE DATABASE {db_name}
                WITH OWNER = {db_user}
                ENCODING = 'UTF8'
                LC_COLLATE = 'en_US.UTF-8'
                LC_CTYPE = 'en_US.UTF-8'
                TEMPLATE template0
            """)
            print(f"База данных {db_name} создана")
        else:
            print(f"База данных {db_name} уже существует")
        
        # Даем права пользователю
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
        
        cursor.close()
        conn.close()
        
        print("\n Инициализация базы данных завершена успешно!")
        print(f"   База данных: {db_name}")
        print(f"   Пользователь: {db_user}")
        print(f"   Строка подключения: postgresql://{db_user}:{db_password}@{host}:{port}/{db_name}")
        
    except Exception as e:
        print(f" Ошибка при инициализации базы данных: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()