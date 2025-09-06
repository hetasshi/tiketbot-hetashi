"""
Модель уведомления пользователя.
"""

import enum
from typing import Optional
import uuid

from sqlalchemy import String, Text, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class NotificationType(enum.Enum):
    """Типы уведомлений."""
    
    NEW_TICKET = "NEW_TICKET"               # Новый тикет создан
    TICKET_ASSIGNED = "TICKET_ASSIGNED"     # Тикет назначен
    TICKET_STATUS_CHANGED = "TICKET_STATUS_CHANGED"  # Статус тикета изменен
    NEW_MESSAGE = "NEW_MESSAGE"             # Новое сообщение в тикете
    TICKET_CLOSED = "TICKET_CLOSED"         # Тикет закрыт
    SYSTEM = "SYSTEM"                       # Системное уведомление
    
    def __str__(self):
        return self.value
    
    @property
    def display_name(self) -> str:
        """Отображаемое название типа уведомления на русском."""
        names = {
            NotificationType.NEW_TICKET: "Новый тикет",
            NotificationType.TICKET_ASSIGNED: "Тикет назначен",
            NotificationType.TICKET_STATUS_CHANGED: "Статус изменен",
            NotificationType.NEW_MESSAGE: "Новое сообщение",
            NotificationType.TICKET_CLOSED: "Тикет закрыт",
            NotificationType.SYSTEM: "Системное уведомление"
        }
        return names[self]
    
    @property
    def icon(self) -> str:
        """Иконка типа уведомления."""
        icons = {
            NotificationType.NEW_TICKET: "🎫",
            NotificationType.TICKET_ASSIGNED: "👤",
            NotificationType.TICKET_STATUS_CHANGED: "🔄",
            NotificationType.NEW_MESSAGE: "💬",
            NotificationType.TICKET_CLOSED: "✅",
            NotificationType.SYSTEM: "⚡"
        }
        return icons[self]
    
    @property
    def priority(self) -> int:
        """Приоритет уведомления для сортировки (больше = важнее)."""
        priorities = {
            NotificationType.SYSTEM: 5,
            NotificationType.NEW_TICKET: 4,
            NotificationType.TICKET_ASSIGNED: 4,
            NotificationType.NEW_MESSAGE: 3,
            NotificationType.TICKET_STATUS_CHANGED: 2,
            NotificationType.TICKET_CLOSED: 1
        }
        return priorities[self]


class Notification(BaseModel):
    """Модель уведомления пользователя."""
    
    __tablename__ = "notifications"
    
    # Получатель уведомления
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID получателя уведомления"
    )
    
    # Связанный тикет (опционально)
    ticket_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID связанного тикета"
    )
    
    # Тип уведомления
    type: Mapped[NotificationType] = mapped_column(
        Enum(NotificationType),
        nullable=False,
        index=True,
        comment="Тип уведомления"
    )
    
    # Содержание уведомления
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Заголовок уведомления"
    )
    
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Содержание уведомления"
    )
    
    # Статус прочтения
    is_read: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Прочитано ли уведомление"
    )
    
    # Связи с другими моделями
    user = relationship("User", back_populates="notifications")
    ticket = relationship("Ticket", back_populates="notifications")
    
    @property
    def display_title(self) -> str:
        """Отображаемый заголовок с иконкой."""
        return f"{self.type.icon} {self.title}"
    
    @property
    def short_content(self) -> str:
        """Короткое содержание (первые 100 символов)."""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."
    
    def mark_as_read(self) -> None:
        """Пометить уведомление как прочитанное."""
        self.is_read = True
    
    def can_be_viewed_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь просматривать уведомление.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может просматривать
        """
        # Только получатель может просматривать свои уведомления
        return self.user_id == user.id
    
    def can_be_deleted_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь удалять уведомление.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может удалять
        """
        # Получатель может удалять свои уведомления
        if self.user_id == user.id:
            return True
        
        # Администраторы могут удалять любые уведомления
        from .user import UserRole
        return user.role.can_access(UserRole.ADMIN)
    
    @classmethod
    def create_new_ticket_notification(
        cls, 
        user_id: uuid.UUID, 
        ticket_id: uuid.UUID, 
        ticket_title: str
    ) -> dict:
        """
        Создать уведомление о новом тикете.
        
        Args:
            user_id: ID получателя (персонал)
            ticket_id: ID тикета
            ticket_title: Заголовок тикета
            
        Returns:
            Данные для создания уведомления
        """
        return {
            "user_id": user_id,
            "ticket_id": ticket_id,
            "type": NotificationType.NEW_TICKET,
            "title": "Новый тикет поддержки",
            "content": f"Создан новый тикет: {ticket_title}"
        }
    
    @classmethod
    def create_ticket_assigned_notification(
        cls, 
        user_id: uuid.UUID, 
        ticket_id: uuid.UUID, 
        ticket_title: str,
        assigner_name: str
    ) -> dict:
        """
        Создать уведомление о назначении тикета.
        
        Args:
            user_id: ID назначенного сотрудника
            ticket_id: ID тикета
            ticket_title: Заголовок тикета
            assigner_name: Имя назначившего
            
        Returns:
            Данные для создания уведомления
        """
        return {
            "user_id": user_id,
            "ticket_id": ticket_id,
            "type": NotificationType.TICKET_ASSIGNED,
            "title": "Тикет назначен на вас",
            "content": f"Вам назначен тикет '{ticket_title}' пользователем {assigner_name}"
        }
    
    @classmethod
    def create_new_message_notification(
        cls, 
        user_id: uuid.UUID, 
        ticket_id: uuid.UUID, 
        ticket_title: str,
        sender_name: str,
        message_preview: str
    ) -> dict:
        """
        Создать уведомление о новом сообщении.
        
        Args:
            user_id: ID получателя
            ticket_id: ID тикета
            ticket_title: Заголовок тикета
            sender_name: Имя отправителя
            message_preview: Превью сообщения
            
        Returns:
            Данные для создания уведомления
        """
        return {
            "user_id": user_id,
            "ticket_id": ticket_id,
            "type": NotificationType.NEW_MESSAGE,
            "title": "Новое сообщение в тикете",
            "content": f"{sender_name} ответил в тикете '{ticket_title}': {message_preview}"
        }
    
    @classmethod
    def create_status_changed_notification(
        cls, 
        user_id: uuid.UUID, 
        ticket_id: uuid.UUID, 
        ticket_title: str,
        old_status: str,
        new_status: str
    ) -> dict:
        """
        Создать уведомление об изменении статуса тикета.
        
        Args:
            user_id: ID получателя
            ticket_id: ID тикета
            ticket_title: Заголовок тикета
            old_status: Старый статус
            new_status: Новый статус
            
        Returns:
            Данные для создания уведомления
        """
        return {
            "user_id": user_id,
            "ticket_id": ticket_id,
            "type": NotificationType.TICKET_STATUS_CHANGED,
            "title": "Статус тикета изменен",
            "content": f"Статус тикета '{ticket_title}' изменен с '{old_status}' на '{new_status}'"
        }
    
    def __str__(self) -> str:
        return f"Notification {self.type.display_name} for user {self.user_id}"