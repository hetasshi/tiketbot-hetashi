"""
Модель пользователя системы.
"""

import enum
from typing import Optional

from sqlalchemy import BigInteger, String, Boolean, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class UserRole(enum.Enum):
    """Роли пользователей в системе."""
    
    USER = "USER"                    # Обычный пользователь
    HELPER = "HELPER"               # Помощник поддержки
    MODERATOR = "MODERATOR"         # Модератор
    ADMIN = "ADMIN"                 # Администратор
    DEVELOPER = "DEVELOPER"         # Разработчик (высший уровень)
    
    def __str__(self):
        return self.value
    
    @property
    def level(self) -> int:
        """Числовой уровень роли для сравнения прав доступа."""
        levels = {
            UserRole.USER: 1,
            UserRole.HELPER: 2,
            UserRole.MODERATOR: 3,
            UserRole.ADMIN: 4,
            UserRole.DEVELOPER: 5
        }
        return levels[self]
    
    def can_access(self, required_role: 'UserRole') -> bool:
        """Проверка, может ли данная роль получить доступ к функции."""
        return self.level >= required_role.level


class User(BaseModel):
    """Модель пользователя Telegram."""
    
    __tablename__ = "users"
    
    # Telegram данные
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
        comment="ID пользователя в Telegram"
    )
    
    username: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
        comment="Username в Telegram (@username)"
    )
    
    # Личные данные
    first_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Имя пользователя"
    )
    
    last_name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Фамилия пользователя"
    )
    
    # Системные данные
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.USER,
        index=True,
        comment="Роль пользователя в системе"
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Активен ли пользователь"
    )
    
    # Дополнительные данные
    avatar_url: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        comment="URL аватарки пользователя"
    )
    
    language_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="ru",
        comment="Код языка интерфейса"
    )
    
    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Premium статус в Telegram"
    )
    
    # Связи с другими моделями
    tickets = relationship("Ticket", foreign_keys="Ticket.user_id", back_populates="user")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_to", back_populates="assigned_user")
    messages = relationship("Message", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    
    @property
    def full_name(self) -> str:
        """Полное имя пользователя."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    @property
    def display_name(self) -> str:
        """Отображаемое имя пользователя."""
        if self.username:
            return f"@{self.username}"
        return self.full_name
    
    def can_access_admin_panel(self) -> bool:
        """Проверка доступа к админ-панели."""
        return self.role.can_access(UserRole.MODERATOR)
    
    def can_assign_tickets(self) -> bool:
        """Проверка права назначать тикеты."""
        return self.role.can_access(UserRole.HELPER)
    
    def can_manage_users(self) -> bool:
        """Проверка права управлять пользователями."""
        return self.role.can_access(UserRole.ADMIN)
    
    def can_manage_system(self) -> bool:
        """Проверка права управлять системными настройками."""
        return self.role.can_access(UserRole.DEVELOPER)
    
    def __str__(self) -> str:
        return f"User {self.display_name} ({self.role.value})"