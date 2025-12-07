"""
Unit-тесты для моделей данных
"""
import pytest
from datetime import datetime
from src.models.book import Book
from src.models.user import User, UserRole
from src.models.reservation import Reservation, ReservationStatus


class TestBookModel:
    """Тесты для модели Book"""
    
    def test_book_creation(self):
        """Тест создания книги"""
        book = Book(
            id=1,
            title="Преступление и наказание",
            author="Фёдор Достоевский",
            year=1866,
            isbn="978-5-17-090666-7",
            publisher="АСТ",
            genre="Художественная литература",
            pages=672,
            quantity=5,
            available=3
        )
        
        assert book.id == 1
        assert book.title == "Преступление и наказание"
        assert book.author == "Фёдор Достоевский"
        assert book.year == 1866
        assert book.isbn == "978-5-17-090666-7"
        assert book.publisher == "АСТ"
        assert book.genre == "Художественная литература"
        assert book.pages == 672
        assert book.quantity == 5
        assert book.available == 3
        assert book.is_active is True
        assert isinstance(book.created_at, datetime)
    
    def test_book_to_dict(self):
        """Тест преобразования книги в словарь"""
        book = Book(
            id=2,
            title="Война и мир",
            author="Лев Толстой",
            year=1869,
            isbn="978-5-389-06256-1",
            publisher="Азбука",
            genre="Роман",
            pages=1225,
            quantity=3,
            available=1
        )
        
        book_dict = book.to_dict()
        
        assert book_dict['id'] == 2
        assert book_dict['title'] == "Война и мир"
        assert book_dict['author'] == "Лев Толстой"
        assert book_dict['year'] == 1869
        assert book_dict['isbn'] == "978-5-389-06256-1"
        assert book_dict['quantity'] == 3
        assert book_dict['available'] == 1
        assert book_dict['is_active'] is True
    
    def test_book_borrow_success(self):
        """Тест успешного взятия книги"""
        book = Book(id=1, title="Test", author="Test", year=2023, isbn="123", 
                   publisher="Test", genre="Test", pages=100, quantity=3, available=2)
        
        assert book.borrow() is True
        assert book.available == 1
    
    def test_book_borrow_failure(self):
        """Тест неудачного взятия книги (нет в наличии)"""
        book = Book(id=1, title="Test", author="Test", year=2023, isbn="123", 
                   publisher="Test", genre="Test", pages=100, quantity=3, available=0)
        
        assert book.borrow() is False
        assert book.available == 0
    
    def test_book_return(self):
        """Тест возврата книги"""
        book = Book(id=1, title="Test", author="Test", year=2023, isbn="123", 
                   publisher="Test", genre="Test", pages=100, quantity=3, available=1)
        
        book.return_book()
        assert book.available == 2
    
    def test_book_write_off(self):
        """Тест списания книги"""
        book = Book(id=1, title="Test", author="Test", year=2023, isbn="123", 
                   publisher="Test", genre="Test", pages=100, quantity=3, available=2)
        
        book.write_off()
        assert book.is_active is False
        assert book.available == 0


class TestUserModel:
    """Тесты для модели User"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            id=1,
            username="ivanov",
            email="ivanov@example.com",
            password_hash="hashed_password",
            role=UserRole.READER,
            full_name="Иванов Иван Иванович",
            phone="+79161234567"
        )
        
        assert user.id == 1
        assert user.username == "ivanov"
        assert user.email == "ivanov@example.com"
        assert user.password_hash == "hashed_password"
        assert user.role == UserRole.READER
        assert user.full_name == "Иванов Иван Иванович"
        assert user.phone == "+79161234567"
        assert user.is_active is True
        assert isinstance(user.created_at, datetime)
    
    def test_admin_user(self):
        """Тест пользователя-администратора"""
        admin = User(
            id=2,
            username="admin",
            email="admin@library.ru",
            password_hash="admin_hash",
            role=UserRole.ADMIN,
            full_name="Администратор Системы"
        )
        
        assert admin.is_admin() is True
        assert admin.can_borrow() is False  # Админы не могут брать книги
    
    def test_reader_user(self):
        """Тест пользователя-читателя"""
        reader = User(
            id=3,
            username="reader",
            email="reader@example.com",
            password_hash="reader_hash",
            role=UserRole.READER,
            full_name="Читатель Тестовый"
        )
        
        assert reader.is_admin() is False
        assert reader.can_borrow() is True
    
    def test_user_to_dict(self):
        """Тест преобразования пользователя в словарь"""
        user = User(
            id=4,
            username="testuser",
            email="test@example.com",
            password_hash="hash",
            role=UserRole.READER,
            full_name="Тест Юзер"
        )
        
        user_dict = user.to_dict()
        
        assert user_dict['id'] == 4
        assert user_dict['username'] == "testuser"
        assert user_dict['email'] == "test@example.com"
        assert user_dict['role'] == "reader"
        assert user_dict['full_name'] == "Тест Юзер"
        assert 'password_hash' not in user_dict  # Пароль не должен быть в словаре


class TestReservationModel:
    """Тесты для модели Reservation"""
    
    def test_reservation_creation(self):
        """Тест создания бронирования"""
        reservation = Reservation(
            id=1,
            book_id=101,
            user_id=201,
            status=ReservationStatus.PENDING,
            reservation_date=datetime(2024, 1, 15, 10, 30, 0)
        )
        
        assert reservation.id == 1
        assert reservation.book_id == 101
        assert reservation.user_id == 201
        assert reservation.status == ReservationStatus.PENDING
        assert reservation.reservation_date.year == 2024
        assert reservation.pickup_deadline is None
    
    def test_reservation_confirm(self):
        """Тест подтверждения бронирования"""
        reservation = Reservation(
            id=2,
            book_id=102,
            user_id=202,
            status=ReservationStatus.PENDING,
            reservation_date=datetime.now()
        )
        
        pickup_deadline = datetime(2024, 1, 18, 18, 0, 0)
        reservation.confirm(pickup_deadline)
        
        assert reservation.status == ReservationStatus.CONFIRMED
        assert reservation.pickup_deadline == pickup_deadline
    
    def test_reservation_cancel(self):
        """Тест отмены бронирования"""
        reservation = Reservation(
            id=3,
            book_id=103,
            user_id=203,
            status=ReservationStatus.PENDING,
            reservation_date=datetime.now()
        )
        
        reservation.cancel()
        assert reservation.status == ReservationStatus.CANCELLED
    
    def test_reservation_complete(self):
        """Тест завершения бронирования"""
        reservation = Reservation(
            id=4,
            book_id=104,
            user_id=204,
            status=ReservationStatus.CONFIRMED,
            reservation_date=datetime.now()
        )
        
        reservation.complete()
        assert reservation.status == ReservationStatus.COMPLETED
    
    def test_reservation_expired(self):
        """Тест проверки истечения срока брони"""
        from datetime import datetime, timedelta
        
        # Прошедшая дата
        old_date = datetime.now() - timedelta(days=1)
        reservation = Reservation(
            id=5,
            book_id=105,
            user_id=205,
            status=ReservationStatus.CONFIRMED,
            reservation_date=datetime.now() - timedelta(days=5),
            pickup_deadline=old_date
        )
        
        assert reservation.is_expired() is True
    
    def test_reservation_not_expired(self):
        """Тест проверки, что срок брони не истек"""
        from datetime import datetime, timedelta
        
        # Будущая дата
        future_date = datetime.now() + timedelta(days=1)
        reservation = Reservation(
            id=6,
            book_id=106,
            user_id=206,
            status=ReservationStatus.CONFIRMED,
            reservation_date=datetime.now(),
            pickup_deadline=future_date
        )
        
        assert reservation.is_expired() is False
