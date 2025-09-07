"""
Сервис для работы с категориями тикетов.
"""

import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tikethet.models.category import Category


class CategoryService:
    """Сервис для управления категориями тикетов."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_category_by_id(self, category_id: uuid.UUID) -> Optional[Category]:
        """
        Получение категории по ID.
        
        Args:
            category_id: ID категории
            
        Returns:
            Optional[Category]: Категория или None
        """
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_categories(self) -> List[Category]:
        """
        Получение всех активных категорий.
        
        Returns:
            List[Category]: Список активных категорий
        """
        result = await self.db.execute(
            select(Category)
            .where(Category.is_active == True)
            .order_by(Category.sort_order, Category.name)
        )
        return result.scalars().all()
    
    async def create_category(self, category_data: dict) -> Category:
        """
        Создание новой категории.
        
        Args:
            category_data: Данные категории
            
        Returns:
            Category: Созданная категория
        """
        category = Category(**category_data)
        
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        
        return category
    
    async def create_default_categories(self) -> List[Category]:
        """
        Создание категорий по умолчанию для Minecraft проектов.
        
        Returns:
            List[Category]: Созданные категории
        """
        categories = []
        default_categories = Category.get_default_categories()
        
        for category_data in default_categories:
            # Проверяем, не существует ли уже категория с таким именем
            existing = await self.db.execute(
                select(Category).where(Category.name == category_data["name"])
            )
            if existing.scalar_one_or_none():
                continue
            
            category = await self.create_category(category_data)
            categories.append(category)
        
        return categories