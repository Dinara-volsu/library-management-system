"""
Модель пользователя системы
"""
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class UserRole(Enum):
    """Роли пользователей"""
    READER = "reader"
    ADMIN = "admin"


@dataclass
class User:
    """Класс, представляющий пользователя"""
    id: int
    username: str
    email: str
    password_hash: str
    role: UserRole
    full_name: str
    phone: Optional[str] = None
    is_active: bool = True
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def is_admin(self) -> bool:
        """Проверить, является ли пользователь администратором"""
        return self.role == UserRole.ADMIN
    
    def can_borrow(self) -> bool:
        """Может ли пользователь брать книги"""
        return self.is_active and self.role == UserRole.READER
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь (без пароля)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'full_name': self.full_name,
            'phone': self.phone,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
