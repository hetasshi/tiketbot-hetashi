"""
Модель категории тикетов.
"""

from typing import Optional

from sqlalchemy import String, Boolean, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel


class Category(BaseModel):
    """Модель категории тикетов."""
    
    __tablename__ = "categories"
    
    # Основная информация
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Название категории"
    )
    
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Описание категории"
    )
    
    # Визуальное оформление
    icon: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Эмодзи иконка категории"
    )
    
    color: Mapped[str] = mapped_column(
        String(7),
        nullable=False,
        comment="HEX цвет категории (#RRGGBB)"
    )
    
    # Системные настройки
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Активна ли категория"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        index=True,
        comment="Порядок сортировки (меньше = выше)"
    )
    
    # Связи с другими моделями
    tickets = relationship("Ticket", back_populates="category")
    
    @property
    def display_name(self) -> str:
        """Отображаемое название с иконкой."""
        return f"{self.icon} {self.name}"
    
    def __str__(self) -> str:
        return f"Category {self.display_name}"
    
    @classmethod
    def get_default_categories(cls) -> list[dict]:
        """
        Получить список категорий по умолчанию для Minecraft проектов.
        
        Returns:
            Список словарей с данными категорий
        """
        return [
            {
                "name": "Технические проблемы",
                "description": "Проблемы с подключением, лагами, вылетами из игры",
                "icon": "🔧",
                "color": "#FF6B6B",
                "sort_order": 1
            },
            {
                "name": "Баны и наказания", 
                "description": "Вопросы по блокировкам, разбаны, апелляции",
                "icon": "⚖️",
                "color": "#4ECDC4",
                "sort_order": 2
            },
            {
                "name": "Игровые вопросы",
                "description": "Помощь по игровому процессу, командам, механикам",
                "icon": "🎮",
                "color": "#45B7D1",
                "sort_order": 3
            },
            {
                "name": "Экономика и донат",
                "description": "Проблемы с покупками, валютой, привилегиями",
                "icon": "💰",
                "color": "#96CEB4",
                "sort_order": 4
            },
            {
                "name": "Жалобы на игроков",
                "description": "Нарушения правил, читерство, неадекватное поведение",
                "icon": "🚨", 
                "color": "#FECA57",
                "sort_order": 5
            },
            {
                "name": "Другое",
                "description": "Прочие вопросы, не подходящие под остальные категории",
                "icon": "❓",
                "color": "#B8B8B8",
                "sort_order": 6
            }
        ]