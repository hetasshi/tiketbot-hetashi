"""
Схемы для категорий тикетов.
"""

from typing import Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    """Схема ответа с данными категории."""
    
    id: uuid.UUID = Field(description="ID категории")
    name: str = Field(description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    icon: str = Field(description="Эмодзи иконка")
    color: str = Field(description="HEX цвет")
    is_active: bool = Field(description="Активна ли категория")
    sort_order: int = Field(description="Порядок сортировки")
    created_at: datetime = Field(description="Дата создания")
    updated_at: datetime = Field(description="Дата обновления")
    
    # Computed field
    display_name: str = Field(description="Отображаемое название с иконкой")
    
    model_config = {"from_attributes": True}