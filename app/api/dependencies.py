"""
Dependencies для FastAPI endpoints.
"""

import jwt
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db_session
from app.models.user import User, UserRole
from app.services.user_service import UserService

settings = get_settings()
security = HTTPBearer()


class AuthDependencies:
    """Dependencies для аутентификации."""
    
    @staticmethod
    async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: AsyncSession = Depends(get_db_session)
    ) -> User:
        """
        Получение текущего пользователя из JWT токена.
        
        Args:
            credentials: HTTP Bearer токен
            db: Сессия базы данных
            
        Returns:
            User: Текущий пользователь
            
        Raises:
            HTTPException: Если токен недействительный или пользователь не найден
        """
        token = credentials.credentials
        
        try:
            # Декодирование JWT токена
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            # Извлечение данных из токена
            user_id: str = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Недействительный токен"
                )
            
            # Проверка срока действия
            exp = payload.get("exp")
            if exp is None or datetime.utcnow().timestamp() > exp:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Токен истек"
                )
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен истек"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный токен"
            )
        
        # Получение пользователя из базы данных
        user_service = UserService(db)
        user = await user_service.get_user_by_id(user_id)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Аккаунт заблокирован"
            )
        
        return user
    
    @staticmethod
    def require_role(min_role: UserRole):
        """
        Dependency factory для проверки минимального уровня роли.
        
        Args:
            min_role: Минимально необходимая роль
            
        Returns:
            Функция dependency, которая проверяет роль пользователя
        """
        def role_checker(current_user: User = Depends(AuthDependencies.get_current_user)) -> User:
            if not current_user.role.can_access(min_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Недостаточно прав доступа"
                )
            return current_user
        
        return role_checker
    
    @staticmethod
    def get_current_user_optional(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
        db: AsyncSession = Depends(get_db_session)
    ) -> Optional[User]:
        """
        Получение текущего пользователя (опционально).
        
        Args:
            credentials: HTTP Bearer токен (опционально)
            db: Сессия базы данных
            
        Returns:
            Optional[User]: Пользователь или None если не авторизован
        """
        if not credentials:
            return None
        
        try:
            return AuthDependencies.get_current_user(credentials, db)
        except HTTPException:
            return None


# Convenient aliases для различных ролей
require_user = AuthDependencies.require_role(UserRole.USER)
require_helper = AuthDependencies.require_role(UserRole.HELPER)
require_moderator = AuthDependencies.require_role(UserRole.MODERATOR)
require_admin = AuthDependencies.require_role(UserRole.ADMIN)
require_developer = AuthDependencies.require_role(UserRole.DEVELOPER)