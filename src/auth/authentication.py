"""
Система аутентификации и авторизации
"""
import hashlib
import secrets
from typing import Optional, Tuple
from ..models.user import User, UserRole
from ..database.database_manager import DatabaseManager


class AuthenticationManager:
    """Менеджер аутентификации"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.current_user: Optional[User] = None
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> Tuple[str, str]:
        """Хешировать пароль с солью"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return password_hash, salt
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str, role: UserRole = UserRole.READER, 
                     phone: str = None) -> Optional[User]:
        """Зарегистрировать нового пользователя"""
        # Проверяем, существует ли пользователь
        existing_user = self.db.get_user_by_username(username)
        if existing_user:
            return None
        
        # Хешируем пароль
        password_hash, _ = self.hash_password(password)
        
        # Создаём пользователя
        user = User(
            id=0,  # Будет присвоен при сохранении в БД
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            full_name=full_name,
            phone=phone
        )
        
        # Сохраняем в БД
        user_id = self.db.add_user(user)
        if user_id:
            user.id = user_id
            return user
        
        return None
    
    def login(self, username: str, password: str) -> Optional[User]:
        """Аутентификация пользователя"""
        user = self.db.get_user_by_username(username)
        if not user or not user.is_active:
            return None
        
        # Проверяем пароль (в реальном проекте нужно хранить соль отдельно)
        password_hash, _ = self.hash_password(password)
        if user.password_hash == password_hash:
            self.current_user = user
            return user
        
        return None
    
    def logout(self) -> None:
        """Выход из системы"""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Проверить, аутентифицирован ли пользователь"""
        return self.current_user is not None
    
    def is_admin(self) -> bool:
        """Проверить, является ли текущий пользователь администратором"""
        return self.is_authenticated() and self.current_user.is_admin()
    
    def can_borrow_books(self) -> bool:
        """Может ли пользователь брать книги"""
        return self.is_authenticated() and self.current_user.can_borrow()
