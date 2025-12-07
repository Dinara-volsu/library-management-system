"""
Модель бронирования книги
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ReservationStatus(Enum):
    """Статусы бронирования"""
    PENDING = "pending"      # Ожидает подтверждения
    CONFIRMED = "confirmed"  # Подтверждено
    CANCELLED = "cancelled"  # Отменено
    COMPLETED = "completed"  # Завершено


@dataclass
class Reservation:
    """Класс, представляющий бронирование"""
    id: int
    book_id: int
    user_id: int
    status: ReservationStatus
    reservation_date: datetime
    pickup_deadline: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def confirm(self, pickup_deadline: datetime) -> None:
        """Подтвердить бронирование"""
        self.status = ReservationStatus.CONFIRMED
        self.pickup_deadline = pickup_deadline
    
    def cancel(self) -> None:
        """Отменить бронирование"""
        self.status = ReservationStatus.CANCELLED
    
    def complete(self) -> None:
        """Завершить бронирование"""
        self.status = ReservationStatus.COMPLETED
    
    def is_expired(self) -> bool:
        """Проверить, истекло ли время брони"""
        if self.pickup_deadline:
            return datetime.now() > self.pickup_deadline
        return False
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'status': self.status.value,
            'reservation_date': self.reservation_date.isoformat(),
            'pickup_deadline': self.pickup_deadline.isoformat() if self.pickup_deadline else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
