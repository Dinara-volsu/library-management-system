"""
Конфигурация pytest для тестов
"""
import pytest
import sys
import os
import tempfile
from datetime import datetime

# Добавляем путь к исходным файлам
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database.database_manager import DatabaseManager
from models.book import Book
from models.user import User, UserRole


@pytest.fixture
def temp_database():
    """Фикстура для временной базы данных"""
    # Создаём временный файл БД
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Создаём менеджер БД
    db_manager = DatabaseManager(db_path)
    
    # Добавляем тестовые данные
    _add_test_data(db_manager)
    
    yield db_manager
    
    # Очистка
    db_manager.close()
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def sample_book():
    """Фикстура для тестовой книги"""
    return Book(
        id=1,
        title="Тестовая книга",
        author="Тестовый автор",
        year=2024,
        isbn="TEST-001",
        publisher="Тестовое издательство",
        genre="Тестирование",
        pages=100,
        quantity=5,
        available=3
    )


@pytest.fixture
def sample_user():
    """Фикстура для тестового пользователя"""
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password",
        role=UserRole.READER,
        full_name="Тест Пользователь",
        phone="+79998887766"
    )


@pytest.fixture
def library_api():
    """Фикстура для API библиотеки"""
    from api.library_api import LibraryAPI
    api = LibraryAPI()
    yield api
    api.close()


def _add_test_data(db_manager):
    """Добавление тестовых данных в БД"""
    # Тестовые книги
    test_books = [
        {
            "title": "Мастер и Маргарита",
            "author": "Михаил Булгаков",
            "year": 1967,
            "isbn": "978-5-17-090666-7",
            "publisher": "АСТ",
            "genre": "Художественная литература",
            "pages": 480,
            "quantity": 3,
            "available": 2
        },
        {
            "title": "Преступление и наказание",
            "author": "Фёдор Достоевский",
            "year": 1866,
            "isbn": "978-5-389-06256-1",
            "publisher": "Азбука",
            "genre": "Роман",
            "pages": 672,
            "quantity": 5,
            "available": 3
        },
        {
            "title": "Python для начинающих",
            "author": "Марк Лутц",
            "year": 2022,
            "isbn": "978-5-4461-1677-7",
            "publisher": "Питер",
            "genre": "Программирование",
            "pages": 864,
            "quantity": 10,
            "available": 8
        }
    ]
    
    for book_data in test_books:
        book = Book(id=0, **book_data)
        db_manager.add_book(book)
    
    # Тестовые пользователи
    test_users = [
        {
            "username": "reader1",
            "email": "reader1@example.com",
            "password_hash": "hash1",
            "role": UserRole.READER,
            "full_name": "Иванов Иван",
            "phone": "+79161112233"
        },
        {
            "username": "admin1",
            "email": "admin@library.ru",
            "password_hash": "admin_hash",
            "role": UserRole.ADMIN,
            "full_name": "Петров Пётр",
            "phone": "+79162223344"
        }
    ]
    
    for user_data in test_users:
        user = User(id=0, **user_data)
        db_manager.add_user(user)
