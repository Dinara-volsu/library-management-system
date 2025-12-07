"""
Модель книги для системы каталога
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Book:
    """Класс, представляющий книгу в каталоге"""
    id: int
    title: str
    author: str
    year: int
    isbn: str
    publisher: str
    genre: str
    pages: int
    quantity: int
    available: int
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def borrow(self) -> bool:
        """Взять книгу в аренду"""
        if self.available > 0:
            self.available -= 1
            return True
        return False
    
    def return_book(self) -> None:
        """Вернуть книгу"""
        if self.available < self.quantity:
            self.available += 1
    
    def write_off(self) -> None:
        """Списать книгу"""
        self.is_active = False
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'year': self.year,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'genre': self.genre,
            'pages': self.pages,
            'quantity': self.quantity,
            'available': self.available,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
