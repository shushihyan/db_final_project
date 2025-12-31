#!/usr/bin/env python3
"""
Скрипт для заполнения базы данных тестовыми данными через REST API.
"""
import requests
import json
from datetime import date, timedelta
import random
import time
from decimal import Decimal

# Lightweight local fake-data generators to avoid the `faker` dependency
FIRST_NAMES = [
    "Alex", "Maria", "John", "Anna", "Michael", "Elena", "David", "Sara",
    "Robert", "Olga", "Daniel", "Nina", "Paul", "Kate", "Mark", "Irene"
]

LAST_NAMES = [
    "Smith", "Johnson", "Brown", "Davis", "Miller", "Wilson", "Taylor",
    "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Lee"
]

WORDS = [
    "time", "world", "day", "night", "book", "system", "data", "design", "code",
    "system", "future", "science", "history", "art", "market", "star", "river",
    "garden", "machine", "dream", "secret", "color", "light", "sound"
]

COMPANIES = [
    "Acme Publishing", "North Star Books", "Blue River Press", "Sunrise Media",
    "Horizon Publishers", "Atlas House"
]

DOMAINS = ["example.com", "mail.com", "books.org", "library.local"]


def gen_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"


def gen_sentence(nb_words=4):
    return " ".join(random.choice(WORDS) for _ in range(max(1, nb_words))).capitalize() + "."


def gen_paragraph(nb_sentences=3):
    return " ".join(gen_sentence(random.randint(4, 10)) for _ in range(max(1, nb_sentences)))


def gen_word():
    return random.choice(WORDS)


def gen_company():
    return random.choice(COMPANIES)


def gen_isbn13():
    # Simple numeric ISBN-like string (not checksum-validated)
    return str(random.randint(10**12, 10**13 - 1))


def parse_relative_date(spec: str):
    # Accepts specs like '-30y', '-90d' or 'today'
    if spec == 'today':
        return date.today()
    if spec.startswith('-'):
        num = int(spec[1:-1])
        unit = spec[-1]
        if unit == 'y':
            return date.today() - timedelta(days=365 * num)
        if unit == 'd':
            return date.today() - timedelta(days=num)
    # fallback
    return date.today()


def gen_date_between(start_date='-30y', end_date='today'):
    start = parse_relative_date(start_date) if isinstance(start_date, str) else start_date
    end = parse_relative_date(end_date) if isinstance(end_date, str) else end_date
    if start > end:
        start, end = end, start
    delta = (end - start).days
    return (start + timedelta(days=random.randint(0, max(0, delta)))).isoformat()


def gen_email(name: str = None):
    if not name:
        name = gen_name()
    local = name.lower().replace(' ', '.')
    domain = random.choice(DOMAINS)
    return f"{local}@{domain}"

BASE_URL = "http://localhost:8000"

def create_test_books(count=50):
    """Создает тестовые книги"""
    genres = ["Fiction", "Science", "Technology", "History", "Biography", 
              "Fantasy", "Mystery", "Romance", "Business", "Art"]
    
    books_created = 0
    
    for i in range(count):
        title = gen_sentence(nb_words=4).rstrip('.')
        author = gen_name()
        book_data = {
            "title": title,
            "author": author,
            "isbn": gen_isbn13(),
            "published_date": gen_date_between(start_date='-30y', end_date='today'),
            "genre": random.choice(genres),
            "price": str(round(random.uniform(5.0, 99.99), 2)),
            "quantity": random.randint(0, 100),
            "description": gen_paragraph(nb_sentences=3),
            "metadata_info": {
                "publisher": gen_company(),
                "pages": random.randint(100, 1000),
                "language": random.choice(["English", "Russian", "Spanish", "French"]),
                "tags": [gen_word() for _ in range(random.randint(1, 5))],
                "edition": random.randint(1, 10),
                "rating": round(random.uniform(1.0, 5.0), 1)
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/books/", json=book_data)
            if response.status_code == 200:
                books_created += 1
                print(f"Создана книга: {book_data['title'][:30]}...")
            else:
                print(f"Ошибка создания книги: {response.status_code}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        # Небольшая пауза, чтобы не перегружать сервер
        time.sleep(0.1)
    
    return books_created

def create_test_orders(book_ids, count=100):
    """Создает тестовые заказы"""
    orders_created = 0
    
    for i in range(count):
        customer_name = gen_name()
        order_data = {
            "book_id": random.choice(book_ids),
            "customer_name": customer_name,
            "customer_email": gen_email(customer_name),
            "order_date": gen_date_between(start_date='-90d', end_date='today'),
            "quantity": random.randint(1, 5),
            "status": random.choice(["pending", "completed", "shipped", "cancelled"])
        }
        
        try:
            response = requests.post(f"{BASE_URL}/books/orders/", json=order_data)
            if response.status_code == 200:
                orders_created += 1
                print(f"Создан заказ: {order_data['customer_name']}")
            else:
                print(f"Ошибка создания заказа: {response.status_code}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        time.sleep(0.1)
    
    return orders_created

def test_api_endpoints():
    """Тестирует основные эндпоинты API"""
    endpoints = [
        ("GET", "/books/", None),
        ("GET", "/books/statistics/genre/", None),
        ("GET", "/books/filter/advanced/?in_stock=true", None),
    ]
    
    for method, endpoint, data in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", json=data)
            
            print(f"{method} {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    print(f"   Получено записей: {len(result)}")
                elif isinstance(result, dict):
                    print(f"   Ответ: {list(result.keys())}")
        except Exception as e:
            print(f"Ошибка тестирования {endpoint}: {e}")

def main():
    print(" Начало заполнения базы данных тестовыми данными")
    print("=" * 50)
    
    # 1. Создаем книги
    print("\n Создание книг...")
    books_created = create_test_books(50)
    print(f" Создано книг: {books_created}")
    
    # 2. Получаем ID созданных книг
    try:
        response = requests.get(f"{BASE_URL}/books/")
        if response.status_code == 200:
            books = response.json()
            book_ids = [book['id'] for book in books]
            
            # 3. Создаем заказы
            print("\n🛒 Создание заказов...")
            orders_created = create_test_orders(book_ids, 30)
            print(f" Создано заказов: {orders_created}")
        else:
            print(" Не удалось получить список книг")
    except Exception as e:
        print(f" Ошибка: {e}")
    
    # 4. Тестируем API
    print("\n Тестирование API эндпоинтов...")
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print(" Заполнение базы данных завершено!")
    print(f"   Всего создано: {books_created} книг, {orders_created} заказов")

if __name__ == "__main__":
    main()