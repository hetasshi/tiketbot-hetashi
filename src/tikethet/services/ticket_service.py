"""
Сервис для работы с тикетами поддержки.
"""

import uuid
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ticket import Ticket, TicketStatus, TicketPriority
from app.models.user import User, UserRole
from app.models.category import Category
from app.models.message import Message
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketFilter
from app.schemas.common import PaginationParams


class TicketService:
    """Сервис для управления тикетами поддержки."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_ticket_by_id(
        self, 
        ticket_id: uuid.UUID, 
        load_relations: bool = True
    ) -> Optional[Ticket]:
        """
        Получение тикета по ID.
        
        Args:
            ticket_id: ID тикета
            load_relations: Загружать ли связанные объекты
            
        Returns:
            Optional[Ticket]: Тикет или None
        """
        query = select(Ticket).where(Ticket.id == ticket_id)
        
        if load_relations:
            query = query.options(
                selectinload(Ticket.user),
                selectinload(Ticket.assigned_user),
                selectinload(Ticket.category),
                selectinload(Ticket.messages).selectinload(Message.user)
            )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_ticket(self, ticket_data: TicketCreate, user: User) -> Ticket:
        """
        Создание нового тикета.
        
        Args:
            ticket_data: Данные для создания тикета
            user: Автор тикета
            
        Returns:
            Ticket: Созданный тикет
        """
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            category_id=ticket_data.category_id,
            priority=ticket_data.priority,
            user_id=user.id,
            status=TicketStatus.OPEN
        )
        
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        
        # Загружаем связанные объекты
        await self.db.refresh(ticket, ["user", "category"])
        
        return ticket
    
    async def update_ticket(
        self, 
        ticket: Ticket, 
        ticket_data: TicketUpdate
    ) -> Ticket:
        """
        Обновление тикета.
        
        Args:
            ticket: Тикет для обновления
            ticket_data: Новые данные
            
        Returns:
            Ticket: Обновленный тикет
        """
        update_data = ticket_data.model_dump(exclude_unset=True)
        
        # Если меняется статус на CLOSED, устанавливаем closed_at
        if "status" in update_data and update_data["status"] == TicketStatus.CLOSED:
            update_data["closed_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(ticket, field, value)
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        return ticket
    
    async def assign_ticket(
        self, 
        ticket: Ticket, 
        assigned_user: Optional[User]
    ) -> Ticket:
        """
        Назначение тикета на пользователя.
        
        Args:
            ticket: Тикет для назначения
            assigned_user: Пользователь для назначения (None для снятия назначения)
            
        Returns:
            Ticket: Обновленный тикет
        """
        ticket.assigned_to = assigned_user.id if assigned_user else None
        
        # Если назначаем тикет и он открыт, меняем статус на "В работе"
        if assigned_user and ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        return ticket
    
    async def get_tickets(
        self,
        filters: TicketFilter,
        pagination: PaginationParams,
        user: User
    ) -> Tuple[List[Ticket], int]:
        """
        Получение списка тикетов с фильтрами и пагинацией.
        
        Args:
            filters: Фильтры для поиска
            pagination: Параметры пагинации
            user: Пользователь, который запрашивает список
            
        Returns:
            Tuple[List[Ticket], int]: (список тикетов, общее количество)
        """
        # Базовый запрос с загрузкой связанных объектов
        base_query = select(Ticket).options(
            selectinload(Ticket.user),
            selectinload(Ticket.assigned_user),
            selectinload(Ticket.category)
        )
        
        # Применяем фильтры доступа
        conditions = []
        
        # Обычные пользователи видят только свои тикеты
        if user.role == UserRole.USER:
            conditions.append(Ticket.user_id == user.id)
        # Персонал видит все тикеты или назначенные на них
        elif user.role.can_access(UserRole.HELPER):
            if filters.user_id:
                conditions.append(Ticket.user_id == filters.user_id)
            if filters.assigned_to:
                conditions.append(Ticket.assigned_to == filters.assigned_to)
        
        # Применяем фильтры
        if filters.status:
            conditions.append(Ticket.status == filters.status)
        
        if filters.priority:
            conditions.append(Ticket.priority == filters.priority)
        
        if filters.category_id:
            conditions.append(Ticket.category_id == filters.category_id)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Ticket.title.ilike(search_term),
                    Ticket.description.ilike(search_term)
                )
            )
        
        # Применяем условия к запросу
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Запрос для подсчета общего количества
        count_query = select(func.count()).select_from(Ticket)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        # Получаем общее количество
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Применяем сортировку и пагинацию
        query = base_query.order_by(
            Ticket.priority.desc(),
            Ticket.created_at.desc()
        ).offset(pagination.skip).limit(pagination.limit)
        
        # Выполняем запрос
        result = await self.db.execute(query)
        tickets = result.scalars().all()
        
        return tickets, total
    
    async def get_user_tickets(
        self,
        user: User,
        status_filter: Optional[TicketStatus] = None,
        pagination: PaginationParams = None
    ) -> Tuple[List[Ticket], int]:
        """
        Получение тикетов пользователя.
        
        Args:
            user: Пользователь
            status_filter: Фильтр по статусу (опционально)
            pagination: Параметры пагинации
            
        Returns:
            Tuple[List[Ticket], int]: (список тикетов, общее количество)
        """
        conditions = [Ticket.user_id == user.id]
        
        if status_filter:
            conditions.append(Ticket.status == status_filter)
        
        # Запрос для подсчета
        count_query = select(func.count()).select_from(Ticket).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Основной запрос
        query = select(Ticket).where(and_(*conditions)).options(
            selectinload(Ticket.category),
            selectinload(Ticket.assigned_user)
        ).order_by(Ticket.created_at.desc())
        
        if pagination:
            query = query.offset(pagination.skip).limit(pagination.limit)
        
        result = await self.db.execute(query)
        tickets = result.scalars().all()
        
        return tickets, total
    
    async def get_assigned_tickets(
        self,
        user: User,
        status_filter: Optional[TicketStatus] = None
    ) -> List[Ticket]:
        """
        Получение тикетов, назначенных на пользователя.
        
        Args:
            user: Пользователь
            status_filter: Фильтр по статусу
            
        Returns:
            List[Ticket]: Список назначенных тикетов
        """
        conditions = [Ticket.assigned_to == user.id]
        
        if status_filter:
            conditions.append(Ticket.status == status_filter)
        
        query = select(Ticket).where(and_(*conditions)).options(
            selectinload(Ticket.user),
            selectinload(Ticket.category)
        ).order_by(Ticket.priority.desc(), Ticket.created_at.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def close_ticket(self, ticket: Ticket) -> Ticket:
        """
        Закрытие тикета.
        
        Args:
            ticket: Тикет для закрытия
            
        Returns:
            Ticket: Закрытый тикет
        """
        ticket.status = TicketStatus.CLOSED
        ticket.closed_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        return ticket
    
    async def reopen_ticket(self, ticket: Ticket) -> Ticket:
        """
        Повторное открытие тикета.
        
        Args:
            ticket: Тикет для открытия
            
        Returns:
            Ticket: Открытый тикет
        """
        ticket.status = TicketStatus.OPEN
        ticket.closed_at = None
        
        await self.db.commit()
        await self.db.refresh(ticket)
        
        return ticket
    
    async def get_tickets_statistics(self, user: Optional[User] = None) -> dict:
        """
        Получение статистики по тикетам.
        
        Args:
            user: Пользователь для фильтрации (опционально)
            
        Returns:
            dict: Статистика по тикетам
        """
        conditions = []
        
        if user and user.role == UserRole.USER:
            conditions.append(Ticket.user_id == user.id)
        elif user and user.role.can_access(UserRole.HELPER):
            # Персонал может видеть статистику по всем или назначенным тикетам
            pass
        
        base_query = select(func.count()).select_from(Ticket)
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Общее количество тикетов
        total_result = await self.db.execute(base_query)
        total = total_result.scalar()
        
        # Статистика по статусам
        status_stats = {}
        for status in TicketStatus:
            status_query = base_query.where(Ticket.status == status)
            result = await self.db.execute(status_query)
            status_stats[status.value] = result.scalar()
        
        # Статистика по приоритетам
        priority_stats = {}
        for priority in TicketPriority:
            priority_query = base_query.where(Ticket.priority == priority)
            result = await self.db.execute(priority_query)
            priority_stats[priority.value] = result.scalar()
        
        return {
            "total": total,
            "by_status": status_stats,
            "by_priority": priority_stats
        }