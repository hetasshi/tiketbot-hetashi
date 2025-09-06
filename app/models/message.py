"""
Модель сообщения в тикете.
"""

from typing import List, Dict, Any, Optional
import uuid

from sqlalchemy import String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Message(BaseModel):
    """Модель сообщения в тикете поддержки."""
    
    __tablename__ = "messages"
    
    # Связи
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID тикета"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID автора сообщения"
    )
    
    # Контент
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="Текст сообщения"
    )
    
    # Вложения (JSON массив с файлами)
    attachments: Mapped[List[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        comment="Массив вложенных файлов"
    )
    
    # Системные поля
    is_internal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Внутренняя заметка персонала (не видна клиенту)"
    )
    
    # Связи с другими моделями
    ticket = relationship("Ticket", back_populates="messages")
    user = relationship("User", back_populates="messages")
    
    @property
    def has_attachments(self) -> bool:
        """Есть ли вложения в сообщении."""
        return bool(self.attachments)
    
    @property
    def attachment_count(self) -> int:
        """Количество вложений."""
        return len(self.attachments)
    
    @property
    def short_content(self) -> str:
        """Короткий текст сообщения (первые 100 символов)."""
        if len(self.content) <= 100:
            return self.content
        return self.content[:97] + "..."
    
    def get_attachments_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """
        Получить вложения определенного типа.
        
        Args:
            file_type: Тип файла (image, document, etc.)
            
        Returns:
            Список вложений указанного типа
        """
        return [
            attachment for attachment in self.attachments
            if attachment.get("type") == file_type
        ]
    
    def get_image_attachments(self) -> List[Dict[str, Any]]:
        """Получить только изображения."""
        image_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        return [
            attachment for attachment in self.attachments
            if attachment.get("content_type") in image_types
        ]
    
    def get_document_attachments(self) -> List[Dict[str, Any]]:
        """Получить только документы."""
        document_types = [
            "application/pdf", "application/msword", 
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "text/plain"
        ]
        return [
            attachment for attachment in self.attachments
            if attachment.get("content_type") in document_types
        ]
    
    def can_be_viewed_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь просматривать сообщение.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может просматривать
        """
        # Внутренние сообщения видят только персонал
        from .user import UserRole
        if self.is_internal and not user.role.can_access(UserRole.HELPER):
            return False
        
        # Остальные сообщения - проверяем доступ к тикету
        return self.ticket.can_be_viewed_by(user)
    
    def can_be_edited_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь редактировать сообщение.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может редактировать
        """
        # Автор может редактировать свои сообщения в течение 5 минут
        if self.user_id == user.id:
            from datetime import datetime, timedelta
            time_limit = self.created_at + timedelta(minutes=5)
            if datetime.now(tz=self.created_at.tzinfo) <= time_limit:
                return True
        
        # Модераторы+ могут редактировать любые сообщения
        from .user import UserRole
        return user.role.can_access(UserRole.MODERATOR)
    
    def can_be_deleted_by(self, user: "User") -> bool:
        """
        Проверка, может ли пользователь удалять сообщение.
        
        Args:
            user: Пользователь для проверки
            
        Returns:
            True если может удалять
        """
        # Только модераторы+ могут удалять сообщения
        from .user import UserRole
        return user.role.can_access(UserRole.MODERATOR)
    
    @classmethod
    def create_attachment_data(
        cls, 
        filename: str, 
        size: int, 
        content_type: str, 
        url: str,
        file_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Создать данные вложения.
        
        Args:
            filename: Имя файла
            size: Размер файла в байтах
            content_type: MIME тип файла
            url: URL для доступа к файлу
            file_id: ID файла в Telegram (опционально)
            
        Returns:
            Словарь с данными вложения
        """
        return {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "size": size,
            "content_type": content_type,
            "url": url,
            "telegram_file_id": file_id,
            "uploaded_at": __import__('datetime').datetime.now().isoformat()
        }
    
    def __str__(self) -> str:
        author_name = self.user.display_name if hasattr(self, 'user') and self.user else "Unknown"
        prefix = "[Internal] " if self.is_internal else ""
        return f"{prefix}Message from {author_name}: {self.short_content}"