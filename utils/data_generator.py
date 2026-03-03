"""
Генератор тестовых данных для нагрузочного тестирования
Использует библиотеку Faker для создания реалистичных имен, email и т.д.
"""
from faker import Faker
import csv
import os
import random

# Создаем объект Faker с русской локалью (будут русские имена)
fake = Faker('ru_RU')

def generate_test_users(count=100, filename='test_users.csv'):
    """
    Генерирует указанное количество тестовых пользователей
    и сохраняет их в CSV файл.
    
    Параметры:
        count: количество пользователей
        filename: имя файла для сохранения
    """
    # Создаем папку data, если её нет
    os.makedirs('data', exist_ok=True)
    
    filepath = os.path.join('data', filename)
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Заголовки столбцов
        writer.writerow(['first_name', 'last_name', 'email', 'password', 'city'])
        
        for i in range(count):
            writer.writerow([
                fake.first_name(),
                fake.last_name(),
                fake.email(),
                fake.password(length=10),
                fake.city()
            ])
    
    print(f"✅ Сгенерировано {count} пользователей в файл {filepath}")
    return filepath

def generate_search_queries(filename='search_queries.csv'):
    """
    Генерирует реалистичные поисковые запросы для интернет-магазина
    """
    os.makedirs('data', exist_ok=True)
    
    # Категории товаров
    categories = ['ноутбук', 'смартфон', 'наушники', 'клавиатура', 'мышь', 'монитор']
    brands = ['apple', 'samsung', 'dell', 'hp', 'lenovo', 'xiaomi']
    
    queries = []
    
    # Простые запросы (категории)
    queries.extend(categories)
    
    # Бренды
    queries.extend(brands)
    
    # Комбинации бренд + категория
    for brand in brands[:3]:
        for category in categories[:3]:
            queries.append(f"{brand} {category}")
    
    # Добавляем запросы с опечатками (имитация реальных пользователей)
    queries.extend(['ноутбу', 'телефон', 'наушни'])
    
    # Сохраняем в файл
    filepath = os.path.join('data', filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        for query in queries:
            f.write(query + '\n')
    
    print(f"✅ Сгенерировано {len(queries)} поисковых запросов")
    return filepath

if __name__ == "__main__":
    print("🚀 Генерация тестовых данных...")
    generate_test_users(50)
    generate_search_queries()
    print("✅ Готово!")