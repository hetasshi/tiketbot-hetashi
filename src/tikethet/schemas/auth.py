"""
Схемы для аутентификации.
"""

from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field

from .user import UserResponse


class TelegramAuth(BaseModel):
    """Схема данных аутентификации Telegram WebApp."""
    
    init_data: str = Field(description="Данные инициализации от Telegram WebApp")


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном."""
    
    access_token: str = Field(description="JWT токен доступа")
    token_type: str = Field("bearer", description="Тип токена")
    expires_at: datetime = Field(description="Время истечения токена")
    user: UserResponse = Field(description="Данные пользователя")


class TokenRefresh(BaseModel):
    """Схема обновления токена."""
    
    refresh_token: str = Field(description="Refresh токен")


class LoginRequest(BaseModel):
    """Схема запроса входа."""
    
    telegram_id: int = Field(description="ID пользователя в Telegram")
    first_name: str = Field(description="Имя пользователя")
    last_name: Optional[str] = Field(None, description="Фамилия пользователя")
    username: Optional[str] = Field(None, description="Username в Telegram")
    language_code: str = Field("ru", description="Код языка")
    is_premium: bool = Field(False, description="Premium статус")