"""
Схемы для пользователей.
"""

from typing import Optional
from datetime import datetime
import uuid

from pydantic import BaseModel, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя."""
    
    telegram_id: int = Field(description="ID пользователя в Telegram")
    username: Optional[str] = Field(None, description="Username в Telegram")
    first_name: str = Field(description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    language_code: str = Field("ru", description="Код языка")
    is_premium: bool = Field(False, description="Premium статус в Telegram")


class UserCreate(UserBase):
    """Схема создания пользователя."""
    pass


class UserUpdate(BaseModel):
    """Схема обновления пользователя."""
    
    username: Optional[str] = Field(None, description="Username в Telegram")
    first_name: Optional[str] = Field(None, description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    language_code: Optional[str] = Field(None, description="Код языка")
    avatar_url: Optional[str] = Field(None, description="URL аватарки")
    is_premium: Optional[bool] = Field(None, description="Premium статус")


class UserResponse(UserBase):
    """Схема ответа с данными пользователя."""
    
    id: uuid.UUID = Field(description="Уникальный ID пользователя")
    role: UserRole = Field(description="Роль пользователя")
    is_active: bool = Field(description="Активен ли пользователь")
    avatar_url: Optional[str] = Field(None, description="URL аватарки")
    created_at: datetime = Field(description="Дата создания")
    updated_at: datetime = Field(description="Дата обновления")
    
    # Computed fields
    full_name: str = Field(description="Полное имя")
    display_name: str = Field(description="Отображаемое имя")
    
    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    """Схема обновления роли пользователя."""
    
    role: UserRole = Field(description="Новая роль пользователя")