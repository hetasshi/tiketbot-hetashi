"""
Базовая модель для всех SQLAlchemy моделей.
"""

import uuid
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column


# Создание базового класса для моделей
Base = declarative_base()


class BaseModel(Base):
    """Базовая модель с общими полями для всех таблиц."""
    
    __abstract__ = True
    
    # Основные поля
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    def to_dict(self, exclude: list = None) -> Dict[str, Any]:
        """
        Конвертация модели в словарь.
        
        Args:
            exclude: Список полей для исключения
            
        Returns:
            Словарь с данными модели
        """
        exclude = exclude or []
        result = {}
        
        for column in self.__table__.columns:
            if column.name not in exclude:
                value = getattr(self, column.name)
                
                # Обработка специальных типов данных
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                elif isinstance(value, uuid.UUID):
                    result[column.name] = str(value)
                else:
                    result[column.name] = value
                    
        return result
    
    def __repr__(self) -> str:
        """Строковое представление модели."""
        return f"<{self.__class__.__name__}(id={self.id})>"