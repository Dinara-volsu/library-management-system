"""
Менеджер базы данных для системы каталога
"""
import sqlite3
from typing import List, Optional, Dict, Any
from pathlib import Path
from ..models.book import Book
from ..models.user import User, UserRole
from ..models.reservation import Reservation, ReservationStatus
import json
from datetime import datetime


class DatabaseManager:
    """Класс для управления базой данных SQLite"""
    
    def __init__(self, db_path: str = "book_catalog.db"):
        self.db_path = db_path
        self.connection = None
        self._initialize_database()
    
    def connect(self) -> sqlite3.Connection:
        """Установить соединение с БД"""
        if not self.connection:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def _initialize_database(self) -> None:
        """Инициализировать таблицы БД"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('reader', 'admin')),
                full_name TEXT NOT NULL,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица книг
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                isbn TEXT UNIQUE NOT NULL,
                publisher TEXT,
                genre TEXT,
                pages INTEGER,
                quantity INTEGER DEFAULT 1,
                available INTEGER DEFAULT 1,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Таблица бронирований
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('pending', 'confirmed', 'cancelled', 'completed')),
                reservation_date TIMESTAMP NOT NULL,
                pickup_deadline TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (book_id) REFERENCES books (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
    
    # === CRUD для книг ===
    
    def add_book(self, book: Book) -> int:
        """Добавить новую книгу"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO books (title, author, year, isbn, publisher, genre, pages, quantity, available)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            book.title, book.author, book.year, book.isbn,
            book.publisher, book.genre, book.pages, book.quantity, book.available
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def search_books(self, query: str = "", **filters) -> List[Book]:
        """Поиск книг по различным критериям"""
        conn = self.connect()
        cursor = conn.cursor()
        
        sql = "SELECT * FROM books WHERE is_active = 1"
        params = []
        
        if query:
            sql += " AND (title LIKE ? OR author LIKE ? OR isbn LIKE ?)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term, search_term])
        
        if filters:
            for field, value in filters.items():
                if value is not None:
                    sql += f" AND {field} = ?"
                    params.append(value)
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        books = []
        for row in rows:
            books.append(Book(
                id=row['id'],
                title=row['title'],
                author=row['author'],
                year=row['year'],
                isbn=row['isbn'],
                publisher=row['publisher'],
                genre=row['genre'],
                pages=row['pages'],
                quantity=row['quantity'],
                available=row['available'],
                is_active=bool(row['is_active']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            ))
        
        return books
    
    def update_book(self, book_id: int, **updates) -> bool:
        """Обновить информацию о книге"""
        if not updates:
            return False
        
        conn = self.connect()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{key} = ?" for key in updates.keys()])
        sql = f"UPDATE books SET {set_clause} WHERE id = ?"
        
        params = list(updates.values())
        params.append(book_id)
        
        cursor.execute(sql, params)
        conn.commit()
        
        return cursor.rowcount > 0
    
    def write_off_book(self, book_id: int) -> bool:
        """Списать книгу"""
        return self.update_book(book_id, is_active=0, available=0)
    
    # === CRUD для пользователей ===
    
    def add_user(self, user: User) -> int:
        """Добавить нового пользователя"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, full_name, phone)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            user.username, user.email, user.password_hash,
            user.role.value, user.full_name, user.phone
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Найти пользователя по имени"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        
        if row:
            return User(
                id=row['id'],
                username=row['username'],
                email=row['email'],
                password_hash=row['password_hash'],
                role=UserRole(row['role']),
                full_name=row['full_name'],
                phone=row['phone'],
                is_active=bool(row['is_active']),
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            )
        return None
    
    # === CRUD для бронирований ===
    
    def create_reservation(self, reservation: Reservation) -> int:
        """Создать новое бронирование"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO reservations (book_id, user_id, status, reservation_date, pickup_deadline)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            reservation.book_id, reservation.user_id,
            reservation.status.value, reservation.reservation_date.isoformat(),
            reservation.pickup_deadline.isoformat() if reservation.pickup_deadline else None
        ))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_user_reservations(self, user_id: int) -> List[Reservation]:
        """Получить бронирования пользователя"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT r.*, b.title as book_title 
            FROM reservations r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = ?
            ORDER BY r.created_at DESC
        ''', (user_id,))
        
        rows = cursor.fetchall()
        reservations = []
        
        for row in rows:
            reservations.append(Reservation(
                id=row['id'],
                book_id=row['book_id'],
                user_id=row['user_id'],
                status=ReservationStatus(row['status']),
                reservation_date=datetime.fromisoformat(row['reservation_date']),
                pickup_deadline=datetime.fromisoformat(row['pickup_deadline']) if row['pickup_deadline'] else None,
                created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None
            ))
        
        return reservations
    
    def close(self) -> None:
        """Закрыть соединение с БД"""
        if self.connection:
            self.connection.close()
            self.connection = None
