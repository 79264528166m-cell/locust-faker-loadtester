"""
Файл сценариев нагрузочного тестирования для веб-сайта
Использует Locust для имитации поведения пользователей
"""
from locust import HttpUser, task, between
import random
import csv
import os

class WebsiteUser(HttpUser):  # ИСПРАВЛЕНО: было HttpTupper, стало HttpUser
    """
    Имитация реального пользователя на сайте.
    Каждый экземпляр класса = один виртуальный пользователь.
    """
    
    # Время ожидания МЕЖДУ задачами (имитация того, что пользователь думает)
    wait_time = between(1, 5)
    
    def on_start(self):
        """
        Что делать, когда пользователь ТОЛЬКО ЗАШЕЛ на сайт.
        Выполняется один раз в начале жизни пользователя.
        """
        print(f"🟢 Пользователь начал сессию")
        
        # Загружаем тестовые данные из CSV
        self.load_test_data()
        
        # Открываем главную страницу при старте
        self.client.get("/")
    
    def on_stop(self):
        """
        Что делать, когда пользователь ПОКИДАЕТ сайт.
        Выполняется один раз в конце.
        """
        print(f"🔴 Пользователь завершил сессию")
    
    def load_test_data(self):
        """
        Загружает тестовые данные из CSV файлов
        """
        # Загружаем пользователей
        self.test_users = []
        users_file = 'data/test_users.csv'
        if os.path.exists(users_file):
            with open(users_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.test_users = list(reader)
            print(f"  Загружено {len(self.test_users)} тестовых пользователей")
        
        # Загружаем поисковые запросы
        self.search_queries = []
        queries_file = 'data/search_queries.csv'
        if os.path.exists(queries_file):
            with open(queries_file, 'r', encoding='utf-8') as f:
                self.search_queries = [line.strip() for line in f.readlines()]
            print(f"  Загружено {len(self.search_queries)} поисковых запросов")
    
    @task(5)
    def view_homepage(self):
        """
        Просмотр главной страницы.
        Вес задачи = 5 (самая частая операция)
        """
        with self.client.get(
            "/", 
            catch_response=True,
            name="Главная страница"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Ошибка {response.status_code}")
            elif len(response.text) < 100:
                response.failure("Страница слишком маленькая (возможно, ошибка)")
    
    @task(4)
    def search_products(self):
        """
        Поиск товаров.
        Вес задачи = 4
        """
        if hasattr(self, 'search_queries') and self.search_queries:
            query = random.choice(self.search_queries)
        else:
            query = random.choice(['ноутбук', 'телефон', 'книга'])
        
        with self.client.get(
            f"/search?q={query}",
            catch_response=True,
            name="Поиск"
        ) as response:
            if response.status_code != 200:
                response.failure(f"Поиск упал: {response.status_code}")
    
    @task(3)
    def view_category(self):
        """
        Просмотр категории товаров
        """
        categories = ['electronics', 'books', 'clothing', 'sports']
        category = random.choice(categories)
        
        self.client.get(
            f"/category/{category}",
            name="Категория"
        )
    
    @task(2)
    def view_product(self):
        """
        Просмотр карточки конкретного товара
        """
        product_id = random.randint(1, 50)
        
        with self.client.get(
            f"/product/{product_id}",
            name="Карточка товара",
            catch_response=True
        ) as response:
            if response.status_code == 404:
                response.failure(f"Товар {product_id} не найден")
    
    @task(1)
    def add_to_cart(self):
        """
        Добавление товара в корзину (редкая операция)
        """
        product_id = random.randint(1, 20)
        
        data = {
            "product_id": product_id,
            "quantity": 1
        }
        
        with self.client.post(
            "/cart/add",
            json=data,
            name="Добавление в корзину",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Не удалось добавить товар: {response.status_code}")
    
    @task(1)
    def login_and_profile(self):
        """
        Авторизация и просмотр личного кабинета (только если есть пользователи)
        """
        if hasattr(self, 'test_users') and self.test_users:
            user = random.choice(self.test_users)
            
            login_data = {
                "email": user['email'],
                "password": user['password']
            }
            
            with self.client.post(
                "/login",
                json=login_data,
                name="Авторизация",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    # Если успешно, заходим в профиль
                    self.client.get("/profile", name="Личный кабинет")
                else:
                    response.failure(f"Не удалось залогиниться: {response.status_code}")