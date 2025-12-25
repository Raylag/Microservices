#!/usr/bin/env python3
"""
Инициализация базы данных для приложения управления пользователями
Создает таблицу users и заполняет ее тестовыми данными
"""

import sqlite3
import os
from datetime import datetime

def init_database():
    """Инициализирует базу данных и создает таблицы"""
    
    # Удаляем старую базу данных, если она существует (для чистоты тестирования)
    if os.path.exists('users.db'):
        print("⚠️  Обнаружена существующая база данных. Удаляю...")
        os.remove('users.db')
        print("✅ Старая база данных удалена")
    
    # Подключаемся к базе данных (она создастся автоматически)
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    
    print("🔧 Создаю таблицу users...")
    
    # Создаем таблицу пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    print("✅ Таблица users создана успешно")
    
    # Добавляем тестовых пользователей
    print("👥 Добавляю тестовых пользователей...")
    
    test_users = [
        # (username, password, full_name, email, status)
        ('admin', 'admin123', 'Администратор Системы', 'admin@company.com', 'active'),
        ('ivan.petrov', 'password123', 'Иван Петров', 'ivan.petrov@example.com', 'active'),
        ('maria.sidorova', 'qwerty456', 'Мария Сидорова', 'maria.sidorova@example.com', 'active'),
        ('alex.volkov', 'letmein789', 'Александр Волков', 'alex.volkov@example.com', 'active'),
        ('olga.ivanova', 'securepass', 'Ольга Иванова', 'olga.ivanova@example.com', 'inactive'),
        ('sergey.kuznetsov', 'testpass', 'Сергей Кузнецов', 'sergey@test.ru', 'blocked'),
        ('ekaterina.smirnova', 'catlover', 'Екатерина Смирнова', 'katya@mail.ru', 'active'),
        ('dmitry.kozlov', 'dima2024', 'Дмитрий Козлов', 'dima@work.com', 'active'),
        ('anna.morozova', 'winter2024', 'Анна Морозова', 'anna.m@company.com', 'inactive'),
        ('maxim.orlov', 'maxpower', 'Максим Орлов', 'max.orlov@example.com', 'active')
    ]
    
    try:
        cursor.executemany('''
            INSERT INTO users (username, password, full_name, email, status) 
            VALUES (?, ?, ?, ?, ?)
        ''', test_users)
        
        connection.commit()
        
        # Получаем количество добавленных пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        print(f"✅ Успешно добавлено {count} тестовых пользователей")
        
        # Выводим информацию о добавленных пользователях
        print("\n📋 Список добавленных пользователей:")
        print("-" * 80)
        print(f"{'ID':<4} {'Username':<20} {'Full Name':<25} {'Status':<12} {'Email':<30}")
        print("-" * 80)
        
        cursor.execute("SELECT id, username, full_name, status, email FROM users ORDER BY id")
        users = cursor.fetchall()
        
        for user in users:
            print(f"{user[0]:<4} {user[1]:<20} {user[2]:<25} {user[3]:<12} {user[4]:<30}")
        
        print("-" * 80)
        
        # Добавляем дополнительную информацию
        cursor.execute("SELECT status, COUNT(*) FROM users GROUP BY status")
        print("\n📊 Статистика по статусам:")
        for status, count in cursor.fetchall():
            print(f"   {status}: {count} пользователей")
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        print(f"\n🔐 Тестовые учетные данные для входа:")
        print(f"   👑 Администратор: логин 'admin', пароль 'admin123'")
        print(f"   👤 Обычный пользователь: логин 'ivan.petrov', пароль 'password123'")
        print(f"   ⚠️  Неактивный пользователь: логин 'olga.ivanova', пароль 'securepass'")
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка при добавлении тестовых данных: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()
    
    return True

def verify_database():
    """Проверяет корректность созданной базы данных"""
    
    if not os.path.exists('users.db'):
        print("❌ База данных не найдена!")
        return False
    
    connection = sqlite3.connect('users.db')
    cursor = connection.cursor()
    
    try:
        # Проверяем структуру таблицы
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("\n🔍 Структура таблицы 'users':")
        print("-" * 60)
        print(f"{'ID':<3} {'Name':<15} {'Type':<15} {'Not Null':<10} {'Default':<15}")
        print("-" * 60)
        
        for col in columns:
            print(f"{col[0]:<3} {col[1]:<15} {col[2]:<15} {col[3]:<10} {str(col[4]):<15}")
        
        print("-" * 60)
        
        # Проверяем наличие данных
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"✅ База данных корректно инициализирована. Всего записей: {count}")
            return True
        else:
            print("❌ База данных пуста!")
            return False
            
    except sqlite3.Error as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False
    finally:
        connection.close()

def main():
    """Основная функция инициализации"""
    
    print("=" * 60)
    print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ ПРИЛОЖЕНИЯ УПРАВЛЕНИЯ ПОЛЬЗОВАТЕЛЯМИ")
    print("=" * 60)
    print("📁 Текущая директория:", os.getcwd())
    print()
    
    # Инициализируем базу данных
    if init_database():
        print("\n" + "=" * 60)
        print("ПРОВЕРКА КОРРЕКТНОСТИ ИНИЦИАЛИЗАЦИИ")
        print("=" * 60)
        
        if verify_database():
            print("\n🎉 База данных успешно инициализирована и готова к использованию!")
            print("\n📝 Далее вы можете:")
            print("   1. Запустить приложение командой: python app.py")
            print("   2. Использовать готовые тестовые учетные записи для входа")
            print("   3. Зарегистрировать новых пользователей через интерфейс")
        else:
            print("\n❌ Проверка базы данных не пройдена!")
    else:
        print("\n❌ Ошибка при инициализации базы данных!")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()