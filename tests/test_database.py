"""
Интеграционные тесты для базы данных
"""
import pytest
import tempfile
import os
from datetime import datetime
from src.database.database_manager import DatabaseManager
from src.models.book import Book
from src.models.user import User, UserRole
from src.models.reservation import Reservation, ReservationStatus


@pytest.fixture
def temp_db():
    """Фикстура для временной базы данных"""
    # Создаём временный файл БД
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    # Создаём менеджер БД
    db_manager = DatabaseManager(db_path)
    yield db_manager
    
    # Убираем за собой
    db_manager.close()
    os.unlink(db_path)


class TestDatabaseManager:
    """Тесты для DatabaseManager"""
    
    def test_database_initialization(self, temp_db):
        """Тест инициализации базы данных"""
        conn = temp_db.connect()
        cursor = conn.cursor()
        
        # Проверяем, что таблицы созданы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'users' in tables
        assert 'books' in tables
        assert 'reservations' in tables
    
    def test_add_and_search_book(self, temp_db):
        """Тест добавления и поиска книги"""
        # Добавляем книгу
        book = Book(
            id=0,
            title="Тестовая книга",
            author="Тестовый автор",
            year=2024,
            isbn="123-456-789",
            publisher="Тест издательство",
            genre="Техническая",
            pages=300,
            quantity=5,
            available=3
        )
        
        book_id = temp_db.add_book(book)
        assert book_id is not None
        
        # Ищем книгу
        books = temp_db.search_books(query="Тестовая")
        assert len(books) == 1
        
        found_book = books[0]
        assert found_book.title == "Тестовая книга"
        assert found_book.author == "Тестовый автор"
        assert found_book.year == 2024
        assert found_book.quantity == 5
        assert found_book.available == 3
    
    def test_search_books_with_filters(self, temp_db):
        """Тест поиска книг с фильтрами"""
        # Добавляем несколько книг
        books_data = [
            ("Книга 1", "Автор 1", 2020, "Фантастика"),
            ("Книга 2", "Автор 1", 2021, "Детектив"),
            ("Книга 3", "Автор 2", 2020, "Фантастика"),
            ("Книга 4", "Автор 3", 2022, "Роман"),
        ]
        
        for i, (title, author, year, genre) in enumerate(books_data):
            book = Book(
                id=0,
                title=title,
                author=author,
                year=year,
                isbn=f"ISBN-{i}",
                publisher="Издательство",
                genre=genre,
                pages=200,
                quantity=3,
                available=2
            )
            temp_db.add_book(book)
        
        # Поиск по автору
        books = temp_db.search_books(author="Автор 1")
        assert len(books) == 2
        
        # Поиск по году
        books = temp_db.search_books(year=2020)
        assert len(books) == 2
        
        # Поиск по жанру
        books = temp_db.search_books(genre="Фантастика")
        assert len(books) == 2
        
        # Комбинированный поиск
        books = temp_db.search_books(author="Автор 1", year=2021)
        assert len(books) == 1
        assert books[0].title == "Книга 2"
    
    def test_add_and_get_user(self, temp_db):
        """Тест добавления и получения пользователя"""
        # Добавляем пользователя
        user = User(
            id=0,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password",
            role=UserRole.READER,
            full_name="Тест Пользователь",
            phone="+79998887766"
        )
        
        user_id = temp_db.add_user(user)
        assert user_id is not None
        
        # Получаем пользователя
        found_user = temp_db.get_user_by_username("testuser")
        assert found_user is not None
        assert found_user.username == "testuser"
        assert found_user.email == "test@example.com"
        assert found_user.full_name == "Тест Пользователь"
        assert found_user.role == UserRole.READER
    
    def test_write_off_book(self, temp_db):
        """Тест списания книги"""
        # Добавляем книгу
        book = Book(
            id=0,
            title="Книга для списания",
            author="Автор",
            year=2000,
            isbn="OLD-123",
            publisher="Издательство",
            genre="Старая",
            pages=100,
            quantity=2,
            available=1
        )
        
        book_id = temp_db.add_book(book)
        
        # Списание книги
        result = temp_db.write_off_book(book_id)
        assert result is True
        
        # Проверяем, что книга не активна
        books = temp_db.search_books(id=book_id)
        assert len(books) == 0  # Не должна находиться в поиске
