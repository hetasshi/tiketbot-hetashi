"""
Модель тикета поддержки.
"""

import enum
from datetime import datetime
from typing import Optional
import uuid

from sqlalchemy import String, Text, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class TicketStatus(enum.Enum):
    """Статусы тикетов."""
    
    OPEN = "OPEN"                           # Открыт (новый)
    IN_PROGRESS = "IN_PROGRESS"             # В работе
    WAITING_RESPONSE = "WAITING_RESPONSE"   # Ожидает ответа клиента
    RESOLVED = "RESOLVED"                   # Решен
    CLOSED = "CLOSED"                       # Закрыт
    
    def __str__(self):
        return self.value
    
    @property
    def display_name(self) -> str:
        """Отображаемое название статуса на русском."""
        names = {
            TicketStatus.OPEN: "Открыт",
            TicketStatus.IN_PROGRESS: "В работе",
            TicketStatus.WAITING_RESPONSE: "Ожидает ответа",
            TicketStatus.RESOLVED: "Решен",
            TicketStatus.CLOSED: "Закрыт"
        }
        return names[self]
    
    @property
    def color(self) -> str:
        """Цвет статуса для UI."""
        colors = {
            TicketStatus.OPEN: "#FF6B6B",
            TicketStatus.IN_PROGRESS: "#4ECDC4",
            TicketStatus.WAITING_RESPONSE: "#FECA57",
            TicketStatus.RESOLVED: "#96CEB4",
            TicketStatus.CLOSED: "#B8B8B8"
        }
        return colors[self]
    
    @property
    def is_active(self) -> bool:
        """Является ли статус активным (не закрытым)."""
        return self in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.WAITING_RESPONSE]


class TicketPriority(enum.Enum):
    """Приоритеты тикетов."""
    
    LOW = "LOW"           # Низкий
    NORMAL = "NORMAL"     # Обычный
    HIGH = "HIGH"         # Высокий
    CRITICAL = "CRITICAL" # Критический
    
    def __str__(self):
        return self.value
    
    @property
    def level(self) -> int:
        """Числовой уровень приоритета для сортировки."""
        levels = {
            TicketPriority.LOW: 1,
            TicketPriority.NORMAL: 2,
            TicketPriority.HIGH: 3,
            TicketPriority.CRITICAL: 4
        }
        return levels[self]
    
    @property
    def display_name(self) -> str:
        """Отображаемое название приоритета на русском."""
        names = {
            TicketPriority.LOW: "Низкий",
            TicketPriority.NORMAL: "Обычный",
            TicketPriority.HIGH: "Высокий",
            TicketPriority.CRITICAL: "Критический"
        }
        return names[self]
    
    @property
    def color(self) -> str:
        """Цвет приоритета для UI."""
        colors = {
            TicketPriority.LOW: "#96CEB4",
            TicketPriority.NORMAL: "#45B7D1",
            TicketPriority.HIGH: "#FECA57",
            TicketPriority.CRITICAL: "#FF6B6B"
        }
        return colors[self]
    
    @property
    def icon(self) -> str:
        """Иконка приоритета."""
        icons = {
            TicketPriority.LOW: "🔵",
            TicketPriority.NORMAL: "🟡",
            TicketPriority.HIGH: "🟠",
            TicketPriority.CRITICAL: "🔴"
        }
        return icons[self]


class Ticket(BaseModel):
    """Модель тикета поддержки."""
    
    __tablename__ = "tickets"
    
    # Связи с пользователями
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID автора тикета"
    )
    
    assigned_to: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID назначенного сотрудника"
    )
    
    # Связь с категорией
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="ID категории тикета"
    )
    
    # Основная информация
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="Заголовок тикета"
    )
    
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Описание проблемы"
    )
    
    # Статус и приоритет
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus),
        nullable=False,
        default=TicketStatus.OPEN,
        index=True,
        comment="Статус тикета"
    )
    
    priority: Mapped[TicketPriority] = mapped_column(
        Enum(TicketPriority),
        nullable=False,
        default=TicketPriority.NORMAL,
        index=True,
        comment="Приоритет тикета"
    )
    
    # Временные метки
    closed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата закрытия тикета"
    )
    
    # Связи с другими моделями (lazy loading)
    user = relationship("User", foreign_keys=[user_id], back_populates="tickets")
    assigned_user = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_tickets")
    category = relationship("Category", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="ticket", cascade="all, delete-orphan")
    
    @property
    def is_active(self) -> bool:
        """Является ли тикет активным."""
        return self.status.is_active
    
    @property
    def is_assigned(self) -> bool:
        """Назначен ли тикет на сотрудника."""
        return self.assigned_to is not None
    
    @property
    def display_title(self) -> str:
        """Отображаемый заголовок с приоритетом."""
        return f"{self.priority.icon} {self.title}"
    
    @property
    def short_description(self) -> str:
        """Короткое описание (первые 100 символов)."""
        if len(self.description) <= 100:
            return self.description
        return self.description[:97] + "..."
    
    def can_be_assigned_to(self, user) -> bool:
        """
        Проверка, может ли тикет быть назначен на пользователя.
        
        Args:
            user: Пользователь для назначения
            
        Returns:
            True если можно назначить
        """
        # Только активные пользователи с ролью HELPER+ могут получать назначения
        from .user import UserRole
        return user.is_active and user.role.can_access(UserRole.HELPER)
    
    def can_be_viewed_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь просматривать тикет.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может просматривать
        """
        # Автор тикета всегда может просматривать
        if self.user_id == user.id:
            return True
        
        # Назначенный сотрудник может просматривать
        if self.assigned_to == user.id:
            return True
        
        # Персонал может просматривать все тикеты
        from .user import UserRole
        return user.role.can_access(UserRole.HELPER)
    
    def can_be_edited_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь редактировать тикет.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может редактировать
        """
        # Автор может редактировать только открытые тикеты
        if self.user_id == user.id and self.status == TicketStatus.OPEN:
            return True
        
        # Персонал может редактировать назначенные им тикеты
        if self.assigned_to == user.id:
            return True
        
        # Модераторы+ могут редактировать любые тикеты
        from .user import UserRole
        return user.role.can_access(UserRole.MODERATOR)
    
    def __str__(self) -> str:
        return f"Ticket #{self.id} - {self.title} ({self.status.display_name})"