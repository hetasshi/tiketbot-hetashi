"""
Общие схемы для API.
"""

from typing import Optional, List, Any
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Параметры пагинации."""
    
    skip: int = Field(0, ge=0, description="Количество элементов для пропуска")
    limit: int = Field(20, ge=1, le=100, description="Максимальное количество элементов")


class PaginatedResponse(BaseModel):
    """Базовая схема для пагинированных ответов."""
    
    items: List[Any]
    total: int = Field(description="Общее количество элементов")
    skip: int = Field(description="Количество пропущенных элементов")
    limit: int = Field(description="Лимит элементов на странице")
    has_more: bool = Field(description="Есть ли еще элементы")
    
    @classmethod
    def create(cls, items: List[Any], total: int, skip: int, limit: int):
        """Создание пагинированного ответа."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total
        )


class ErrorResponse(BaseModel):
    """Схема ошибки API."""
    
    error: str = Field(description="Тип ошибки")
    message: str = Field(description="Сообщение об ошибке")
    details: Optional[dict] = Field(None, description="Дополнительные детали")


class SuccessResponse(BaseModel):
    """Схема успешного ответа."""
    
    success: bool = Field(True)
    message: str = Field(description="Сообщение об успехе")
    data: Optional[dict] = Field(None, description="Дополнительные данные")