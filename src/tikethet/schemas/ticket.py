"""
Схемы для тикетов.
"""

from typing import Optional, List
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.models.ticket import TicketStatus, TicketPriority
from .user import UserResponse
from .category import CategoryResponse
from .common import PaginatedResponse


class TicketBase(BaseModel):
    """Базовая схема тикета."""
    
    title: str = Field(max_length=500, description="Заголовок тикета")
    description: str = Field(description="Описание проблемы")
    category_id: uuid.UUID = Field(description="ID категории")
    priority: TicketPriority = Field(TicketPriority.NORMAL, description="Приоритет")


class TicketCreate(TicketBase):
    """Схема создания тикета."""
    pass


class TicketUpdate(BaseModel):
    """Схема обновления тикета."""
    
    title: Optional[str] = Field(None, max_length=500, description="Заголовок тикета")
    description: Optional[str] = Field(None, description="Описание проблемы")
    priority: Optional[TicketPriority] = Field(None, description="Приоритет")
    status: Optional[TicketStatus] = Field(None, description="Статус тикета")


class TicketAssign(BaseModel):
    """Схема назначения тикета."""
    
    assigned_to: Optional[uuid.UUID] = Field(None, description="ID назначенного пользователя")


class TicketStatusUpdate(BaseModel):
    """Схема обновления статуса тикета."""
    
    status: TicketStatus = Field(description="Новый статус тикета")


class TicketResponse(TicketBase):
    """Схема ответа с данными тикета."""
    
    id: uuid.UUID = Field(description="ID тикета")
    user_id: uuid.UUID = Field(description="ID автора тикета")
    assigned_to: Optional[uuid.UUID] = Field(None, description="ID назначенного пользователя")
    status: TicketStatus = Field(description="Статус тикета")
    created_at: datetime = Field(description="Дата создания")
    updated_at: datetime = Field(description="Дата обновления")
    closed_at: Optional[datetime] = Field(None, description="Дата закрытия")
    
    # Related objects
    user: Optional[UserResponse] = Field(None, description="Автор тикета")
    assigned_user: Optional[UserResponse] = Field(None, description="Назначенный пользователь")
    category: Optional[CategoryResponse] = Field(None, description="Категория")
    
    # Computed fields
    is_active: bool = Field(description="Активен ли тикет")
    is_assigned: bool = Field(description="Назначен ли тикет")
    display_title: str = Field(description="Отображаемый заголовок")
    short_description: str = Field(description="Короткое описание")
    
    model_config = {"from_attributes": True}


class TicketListResponse(PaginatedResponse):
    """Схема ответа со списком тикетов."""
    
    items: List[TicketResponse]


class TicketFilter(BaseModel):
    """Схема фильтров для тикетов."""
    
    status: Optional[TicketStatus] = Field(None, description="Фильтр по статусу")
    priority: Optional[TicketPriority] = Field(None, description="Фильтр по приоритету")
    category_id: Optional[uuid.UUID] = Field(None, description="Фильтр по категории")
    assigned_to: Optional[uuid.UUID] = Field(None, description="Фильтр по назначенному")
    user_id: Optional[uuid.UUID] = Field(None, description="Фильтр по автору")
    search: Optional[str] = Field(None, description="Поиск по заголовку и описанию")