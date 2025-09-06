"""
Сервис для работы с пользователями.
"""

import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Сервис для управления пользователями."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """
        Получение пользователя по ID.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Optional[User]: Пользователь или None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получение пользователя по Telegram ID.
        
        Args:
            telegram_id: ID пользователя в Telegram
            
        Returns:
            Optional[User]: Пользователь или None
        """
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Создание нового пользователя.
        
        Args:
            user_data: Данные для создания пользователя
            
        Returns:
            User: Созданный пользователь
        """
        user = User(
            telegram_id=user_data.telegram_id,
            username=user_data.username,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            language_code=user_data.language_code,
            is_premium=user_data.is_premium,
            role=UserRole.USER  # По умолчанию обычный пользователь
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user(self, user: User, user_data: UserUpdate) -> User:
        """
        Обновление данных пользователя.
        
        Args:
            user: Пользователь для обновления
            user_data: Новые данные
            
        Returns:
            User: Обновленный пользователь
        """
        update_data = user_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_or_create_user(self, user_data: UserCreate) -> tuple[User, bool]:
        """
        Получение существующего пользователя или создание нового.
        
        Args:
            user_data: Данные пользователя
            
        Returns:
            tuple[User, bool]: (пользователь, был_ли_создан)
        """
        existing_user = await self.get_user_by_telegram_id(user_data.telegram_id)
        
        if existing_user:
            # Обновляем данные существующего пользователя
            update_data = UserUpdate(
                username=user_data.username,
                first_name=user_data.first_name,
                last_name=user_data.last_name,
                language_code=user_data.language_code,
                is_premium=user_data.is_premium
            )
            updated_user = await self.update_user(existing_user, update_data)
            return updated_user, False
        
        # Создаем нового пользователя
        new_user = await self.create_user(user_data)
        return new_user, True
    
    async def update_user_role(self, user: User, new_role: UserRole) -> User:
        """
        Обновление роли пользователя.
        
        Args:
            user: Пользователь
            new_role: Новая роль
            
        Returns:
            User: Пользователь с обновленной ролью
        """
        user.role = new_role
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def deactivate_user(self, user: User) -> User:
        """
        Деактивация пользователя.
        
        Args:
            user: Пользователь для деактивации
            
        Returns:
            User: Деактивированный пользователь
        """
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def activate_user(self, user: User) -> User:
        """
        Активация пользователя.
        
        Args:
            user: Пользователь для активации
            
        Returns:
            User: Активированный пользователь
        """
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_users_by_role(self, role: UserRole, limit: int = 100) -> List[User]:
        """
        Получение пользователей с определенной ролью.
        
        Args:
            role: Роль пользователей
            limit: Максимальное количество
            
        Returns:
            List[User]: Список пользователей
        """
        result = await self.db.execute(
            select(User)
            .where(User.role == role)
            .where(User.is_active == True)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_staff_users(self) -> List[User]:
        """
        Получение всех сотрудников (HELPER+).
        
        Returns:
            List[User]: Список сотрудников
        """
        result = await self.db.execute(
            select(User)
            .where(User.role.in_([UserRole.HELPER, UserRole.MODERATOR, UserRole.ADMIN, UserRole.DEVELOPER]))
            .where(User.is_active == True)
        )
        return result.scalars().all()