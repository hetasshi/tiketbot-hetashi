"""
Схемы для сообщений в тикетах.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from .user import UserResponse


class MessageCreate(BaseModel):
    """Схема создания сообщения."""
    
    content: str = Field(description="Текст сообщения")
    attachments: List[Dict[str, Any]] = Field(default=[], description="Вложения")
    is_internal: bool = Field(False, description="Внутренняя заметка персонала")


class MessageUpdate(BaseModel):
    """Схема обновления сообщения."""
    
    content: Optional[str] = Field(None, description="Текст сообщения")


class MessageResponse(MessageCreate):
    """Схема ответа с данными сообщения."""
    
    id: uuid.UUID = Field(description="ID сообщения")
    ticket_id: uuid.UUID = Field(description="ID тикета")
    user_id: uuid.UUID = Field(description="ID автора")
    created_at: datetime = Field(description="Дата создания")
    
    # Related objects
    user: Optional[UserResponse] = Field(None, description="Автор сообщения")
    
    # Computed fields
    has_attachments: bool = Field(description="Есть ли вложения")
    attachment_count: int = Field(description="Количество вложений")
    short_content: str = Field(description="Короткий текст")
    
    model_config = {"from_attributes": True}


class AttachmentData(BaseModel):
    """Схема данных вложения."""
    
    filename: str = Field(description="Имя файла")
    size: int = Field(description="Размер файла в байтах")
    content_type: str = Field(description="MIME тип файла")
    url: str = Field(description="URL для доступа к файлу")
    telegram_file_id: Optional[str] = Field(None, description="ID файла в Telegram")