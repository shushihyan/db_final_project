#!/usr/bin/env python3
"""
Короткий скрипт для тестирования всех запросов API
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None):
    """Тестирует эндпоинт API"""
    try:
        if method == "GET":
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == "POST":
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        elif method == "PUT":
            response = requests.put(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"{method} {endpoint}: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list):
                print(f"    Получено записей: {len(result)}")
                if result:
                    print(f"    Пример: {result[0].get('title', 'N/A')[:30]}...")
            elif isinstance(result, dict):
                print(f"    Успех")
        else:
            print(f"    Ошибка: {response.text[:100]}")
            
    except Exception as e:
        print(f"    Исключение: {e}")

def main():
    print(" Тестирование всех запросов API\n" + "="*50)
    
    # 1. CRUD операции
    print("\n1.  CRUD операции:")
    book_data = {
        "title": "Тестовая книга",
        "author": "Тестовый автор",
        "isbn": "1234567890123",
        "price": "29.99",
        "quantity": 10
    }
    test_endpoint("POST", "/books/", book_data)
    test_endpoint("GET", "/books/")
    
    # 2. SELECT ... WHERE с несколькими условиями
    print("\n2.  SELECT ... WHERE:")
    test_endpoint("GET", "/books/filter/advanced/?in_stock=true&min_price=10")
    
    # 3. JOIN запрос
    print("\n3.  JOIN запрос:")
    test_endpoint("GET", "/books/with-orders/")
    
    # 4. GROUP BY
    print("\n4.  GROUP BY:")
    test_endpoint("GET", "/books/statistics/genre/")
    
    # 5. UPDATE с условием
    print("\n5.  UPDATE с условием:")
    test_endpoint("PUT", "/books/discount/Fiction/?discount_percent=10")
    
    # 6. Поиск по JSON полю
    print("\n6.  Поиск по JSON:")
    test_endpoint("GET", "/books/search/metadata/?q=English")
    
    # 7. Пагинация и сортировка
    print("\n7.  Пагинация и сортировка:")
    test_endpoint("GET", "/books/?skip=0&limit=5&sort_by=title&sort_desc=false")
    
    # 8. Полнотекстовый поиск (если реализован)
    print("\n8.  Полнотекстовый поиск:")
    test_endpoint("GET", "/books/search/fulltext/?q=тест")
    
    # 9. Создание заказа
    print("\n9.  Создание заказа:")
    order_data = {
        "book_id": 1,
        "customer_name": "Иван Иванов",
        "customer_email": "ivan@test.com",
        "order_date": "2025-12-31",
        "quantity": 2
    }
    test_endpoint("POST", "/books/orders/", order_data)
    
    print("\n" + "="*50)
    print(" Тестирование завершено!")

if __name__ == "__main__":
    main()