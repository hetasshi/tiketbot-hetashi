"""
Сервис для аутентификации и работы с JWT токенами.
"""

import hmac
import hashlib
import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import parse_qsl

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate
from app.services.user_service import UserService

settings = get_settings()


class AuthService:
    """Сервис для аутентификации."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_service = UserService(db)
    
    def validate_telegram_data(self, init_data: str, bot_token: str) -> dict:
        """
        Валидация данных от Telegram WebApp.
        
        Args:
            init_data: Строка с данными инициализации от Telegram
            bot_token: Токен бота
            
        Returns:
            dict: Валидированные данные пользователя
            
        Raises:
            ValueError: Если данные не прошли валидацию
        """
        # Парсинг данных
        parsed_data = dict(parse_qsl(init_data))
        
        # Извлечение hash
        provided_hash = parsed_data.pop('hash', None)
        if not provided_hash:
            raise ValueError("Hash не найден в данных")
        
        # Создание строки для проверки
        data_check_string = '\n'.join(
            f"{key}={value}" for key, value in sorted(parsed_data.items())
        )
        
        # Создание HMAC ключа
        secret_key = hmac.new(
            "WebAppData".encode(), 
            bot_token.encode(), 
            hashlib.sha256
        ).digest()
        
        # Вычисление hash
        computed_hash = hmac.new(
            secret_key,
            data_check_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Проверка hash
        if computed_hash != provided_hash:
            raise ValueError("Недействительные данные от Telegram")
        
        # Парсинг данных пользователя
        user_data = parsed_data.get('user', '{}')
        try:
            import json
            user_info = json.loads(user_data)
        except (json.JSONDecodeError, TypeError):
            raise ValueError("Некорректные данные пользователя")
        
        return user_info
    
    def create_access_token(
        self, 
        user_id: uuid.UUID, 
        expires_delta: Optional[timedelta] = None
    ) -> tuple[str, datetime]:
        """
        Создание JWT токена доступа.
        
        Args:
            user_id: ID пользователя
            expires_delta: Время жизни токена
            
        Returns:
            tuple[str, datetime]: (токен, время истечения)
        """
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.jwt_access_token_expire_minutes
            )
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        token = jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return token, expire
    
    async def authenticate_telegram_user(self, init_data: str) -> tuple[User, str, datetime]:
        """
        Аутентификация пользователя через Telegram WebApp.
        
        Args:
            init_data: Данные инициализации от Telegram
            
        Returns:
            tuple[User, str, datetime]: (пользователь, токен, время истечения)
            
        Raises:
            ValueError: Если данные невалидны
        """
        # Валидация данных Telegram
        user_info = self.validate_telegram_data(init_data, settings.telegram_bot_token)
        
        # Создание данных пользователя
        user_data = UserCreate(
            telegram_id=user_info['id'],
            username=user_info.get('username'),
            first_name=user_info['first_name'],
            last_name=user_info.get('last_name'),
            language_code=user_info.get('language_code', 'ru'),
            is_premium=user_info.get('is_premium', False)
        )
        
        # Получение или создание пользователя
        user, created = await self.user_service.get_or_create_user(user_data)
        
        # Создание токена доступа
        access_token, expires_at = self.create_access_token(user.id)
        
        return user, access_token, expires_at
    
    async def authenticate_simple_login(self, login_data: LoginRequest) -> tuple[User, str, datetime]:
        """
        Простая аутентификация пользователя (для тестирования).
        
        Args:
            login_data: Данные для входа
            
        Returns:
            tuple[User, str, datetime]: (пользователь, токен, время истечения)
        """
        # Создание данных пользователя
        user_data = UserCreate(
            telegram_id=login_data.telegram_id,
            username=login_data.username,
            first_name=login_data.first_name,
            last_name=login_data.last_name,
            language_code=login_data.language_code,
            is_premium=login_data.is_premium
        )
        
        # Получение или создание пользователя
        user, created = await self.user_service.get_or_create_user(user_data)
        
        # Создание токена доступа
        access_token, expires_at = self.create_access_token(user.id)
        
        return user, access_token, expires_at
    
    def decode_token(self, token: str) -> dict:
        """
        Декодирование JWT токена.
        
        Args:
            token: JWT токен
            
        Returns:
            dict: Данные из токена
            
        Raises:
            jwt.InvalidTokenError: Если токен недействительный
        """
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
    
    async def get_user_from_token(self, token: str) -> Optional[User]:
        """
        Получение пользователя из JWT токена.
        
        Args:
            token: JWT токен
            
        Returns:
            Optional[User]: Пользователь или None
        """
        try:
            payload = self.decode_token(token)
            user_id = payload.get("sub")
            
            if user_id:
                return await self.user_service.get_user_by_id(uuid.UUID(user_id))
        except jwt.InvalidTokenError:
            pass
        
        return None