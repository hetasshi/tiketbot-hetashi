"""
API endpoints для работы с категориями тикетов.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models.user import User
from app.schemas.category import CategoryResponse
from app.services.category_service import CategoryService
from app.api.dependencies import require_user, require_admin

router = APIRouter()


@router.get("/", response_model=List[CategoryResponse])
async def get_categories(
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение списка активных категорий.
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        List[CategoryResponse]: Список активных категорий
    """
    category_service = CategoryService(db)
    
    categories = await category_service.get_active_categories()
    
    return [
        CategoryResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            icon=category.icon,
            color=category.color,
            is_active=category.is_active,
            sort_order=category.sort_order,
            created_at=category.created_at,
            updated_at=category.updated_at,
            display_name=category.display_name
        )
        for category in categories
    ]


@router.post("/init-defaults")
async def initialize_default_categories(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Создание категорий по умолчанию для Minecraft проектов.
    
    Args:
        current_user: Текущий пользователь (должен быть админом)
        db: Сессия базы данных
        
    Returns:
        dict: Результат операции
    """
    category_service = CategoryService(db)
    
    created_categories = await category_service.create_default_categories()
    
    return {
        "success": True,
        "message": f"Создано {len(created_categories)} категорий по умолчанию",
        "categories": [
            {
                "id": str(category.id),
                "name": category.name,
                "display_name": category.display_name
            }
            for category in created_categories
        ]
    }