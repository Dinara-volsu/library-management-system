"""
API для работы с библиотечной системой
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ..models.book import Book
from ..models.user import User, UserRole
from ..models.reservation import Reservation, ReservationStatus
from ..database.database_manager import DatabaseManager
from ..auth.authentication import AuthenticationManager


class LibraryAPI:
    """Основной API для работы с библиотечной системой"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.auth = AuthenticationManager(self.db)
    
    # === Книги ===
    
    def add_new_book(self, **book_data) -> Optional[Book]:
        """Добавить новую книгу (только для админов)"""
        if not self.auth.is_admin():
            return None
        
        try:
            book = Book(
                id=0,  # Будет присвоен при сохранении
                title=book_data['title'],
                author=book_data['author'],
                year=book_data['year'],
                isbn=book_data['isbn'],
                publisher=book_data.get('publisher', ''),
                genre=book_data.get('genre', ''),
                pages=book_data.get('pages', 0),
                quantity=book_data.get('quantity', 1),
                available=book_data.get('quantity', 1)
            )
            
            book_id = self.db.add_book(book)
            if book_id:
                book.id = book_id
                return book
        except Exception as e:
            print(f"Ошибка при добавлении книги: {e}")
        
        return None
    
    def search_books(self, query: str = "", **filters) -> List[Book]:
        """Поиск книг по различным критериям"""
        return self.db.search_books(query, **filters)
    
    def write_off_book(self, book_id: int) -> bool:
        """Списать книгу (только для админов)"""
        if not self.auth.is_admin():
            return False
        
        return self.db.write_off_book(book_id)
    
    # === Бронирование ===
    
    def reserve_book(self, book_id: int) -> Optional[Reservation]:
        """Забронировать книгу"""
        if not self.auth.can_borrow_books():
            return None
        
        # Проверяем доступность книги
        books = self.db.search_books(id=book_id)
        if not books:
            return None
        
        book = books[0]
        if book.available <= 0:
            return None
        
        # Создаём бронирование
        reservation = Reservation(
            id=0,
            book_id=book_id,
            user_id=self.auth.current_user.id,
            status=ReservationStatus.PENDING,
            reservation_date=datetime.now(),
            pickup_deadline=None
        )
        
        # Сохраняем в БД
        reservation_id = self.db.create_reservation(reservation)
        if reservation_id:
            reservation.id = reservation_id
            
            # Уменьшаем количество доступных книг
            book.borrow()
            self.db.update_book(book_id, available=book.available)
            
            return reservation
        
        return None
    
    def confirm_reservation(self, reservation_id: int) -> bool:
        """Подтвердить бронирование (только для админов)"""
        if not self.auth.is_admin():
            return False
        
        # В реальном проекте здесь была бы логика подтверждения
        # Сейчас просто устанавливаем срок получения
        pickup_deadline = datetime.now() + timedelta(days=3)
        
        # Обновляем статус в БД
        return self.db.update_reservation_status(
            reservation_id, 
            ReservationStatus.CONFIRMED,
            pickup_deadline
        )
    
    def get_my_reservations(self) -> List[Reservation]:
        """Получить мои бронирования"""
        if not self.auth.is_authenticated():
            return []
        
        return self.db.get_user_reservations(self.auth.current_user.id)
    
    # === Пользователи ===
    
    def register(self, username: str, email: str, password: str, 
                full_name: str, phone: str = None) -> Optional[User]:
        """Регистрация нового пользователя"""
        return self.auth.register_user(
            username, email, password, full_name, 
            UserRole.READER, phone
        )
    
    def login(self, username: str, password: str) -> Optional[User]:
        """Вход в систему"""
        return self.auth.login(username, password)
    
    def logout(self) -> None:
        """Выход из системы"""
        self.auth.logout()
    
    def get_current_user(self) -> Optional[User]:
        """Получить текущего пользователя"""
        return self.auth.current_user
    
    def close(self) -> None:
        """Закрыть соединения"""
        self.db.close()
