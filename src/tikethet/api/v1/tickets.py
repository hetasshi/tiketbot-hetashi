"""
API endpoints для работы с тикетами.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tikethet.database import get_db_session
from tikethet.models.user import User, UserRole
from tikethet.models.ticket import TicketStatus, TicketPriority
from tikethet.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketResponse, TicketListResponse,
    TicketFilter, TicketAssign, TicketStatusUpdate
)
from tikethet.schemas.common import PaginationParams, SuccessResponse
from tikethet.services.ticket_service import TicketService
from tikethet.services.category_service import CategoryService
from tikethet.api.dependencies import AuthDependencies, require_user, require_helper

router = APIRouter()


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Создание нового тикета.
    
    Args:
        ticket_data: Данные для создания тикета
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Созданный тикет
    """
    ticket_service = TicketService(db)
    category_service = CategoryService(db)
    
    # Проверяем существование категории
    category = await category_service.get_category_by_id(ticket_data.category_id)
    if not category or not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Указанная категория не найдена или неактивна"
        )
    
    # Создаем тикет
    ticket = await ticket_service.create_ticket(ticket_data, current_user)
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.get("/", response_model=TicketListResponse)
async def get_tickets(
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    priority_filter: Optional[TicketPriority] = Query(None, alias="priority"),
    category_id: Optional[uuid.UUID] = Query(None),
    assigned_to: Optional[uuid.UUID] = Query(None),
    user_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение списка тикетов с фильтрами и пагинацией.
    
    Args:
        status_filter: Фильтр по статусу
        priority_filter: Фильтр по приоритету
        category_id: Фильтр по категории
        assigned_to: Фильтр по назначенному пользователю
        user_id: Фильтр по автору тикета
        search: Поиск по заголовку и описанию
        skip: Количество элементов для пропуска
        limit: Максимальное количество элементов
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketListResponse: Список тикетов с пагинацией
    """
    ticket_service = TicketService(db)
    
    filters = TicketFilter(
        status=status_filter,
        priority=priority_filter,
        category_id=category_id,
        assigned_to=assigned_to,
        user_id=user_id,
        search=search
    )
    
    pagination = PaginationParams(skip=skip, limit=limit)
    
    tickets, total = await ticket_service.get_tickets(filters, pagination, current_user)
    
    # Преобразуем тикеты в response модели
    ticket_responses = [
        TicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            priority=ticket.priority,
            user_id=ticket.user_id,
            assigned_to=ticket.assigned_to,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            closed_at=ticket.closed_at,
            user=ticket.user,
            assigned_user=ticket.assigned_user,
            category=ticket.category,
            is_active=ticket.is_active,
            is_assigned=ticket.is_assigned,
            display_title=ticket.display_title,
            short_description=ticket.short_description
        )
        for ticket in tickets
    ]
    
    return TicketListResponse.create(
        items=ticket_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/my", response_model=TicketListResponse)
async def get_my_tickets(
    status_filter: Optional[TicketStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение тикетов текущего пользователя.
    
    Args:
        status_filter: Фильтр по статусу
        skip: Количество элементов для пропуска
        limit: Максимальное количество элементов
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketListResponse: Список тикетов пользователя
    """
    ticket_service = TicketService(db)
    pagination = PaginationParams(skip=skip, limit=limit)
    
    tickets, total = await ticket_service.get_user_tickets(
        current_user, status_filter, pagination
    )
    
    # Преобразуем в response модели
    ticket_responses = [
        TicketResponse(
            id=ticket.id,
            title=ticket.title,
            description=ticket.description,
            category_id=ticket.category_id,
            priority=ticket.priority,
            user_id=ticket.user_id,
            assigned_to=ticket.assigned_to,
            status=ticket.status,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
            closed_at=ticket.closed_at,
            category=ticket.category,
            assigned_user=ticket.assigned_user,
            is_active=ticket.is_active,
            is_assigned=ticket.is_assigned,
            display_title=ticket.display_title,
            short_description=ticket.short_description
        )
        for ticket in tickets
    ]
    
    return TicketListResponse.create(
        items=ticket_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение тикета по ID.
    
    Args:
        ticket_id: ID тикета
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Данные тикета
    """
    ticket_service = TicketService(db)
    
    ticket = await ticket_service.get_ticket_by_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    # Проверяем права доступа
    if not ticket.can_be_viewed_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра тикета"
        )
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        assigned_user=ticket.assigned_user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.put("/{ticket_id}", response_model=TicketResponse)
async def update_ticket(
    ticket_id: uuid.UUID,
    ticket_data: TicketUpdate,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Обновление тикета.
    
    Args:
        ticket_id: ID тикета
        ticket_data: Данные для обновления
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Обновленный тикет
    """
    ticket_service = TicketService(db)
    
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    # Проверяем права на редактирование
    if not ticket.can_be_edited_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования тикета"
        )
    
    # Обновляем тикет
    ticket = await ticket_service.update_ticket(ticket, ticket_data)
    
    # Загружаем связанные объекты для ответа
    ticket = await ticket_service.get_ticket_by_id(ticket.id)
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        assigned_user=ticket.assigned_user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.post("/{ticket_id}/assign", response_model=TicketResponse)
async def assign_ticket(
    ticket_id: uuid.UUID,
    assign_data: TicketAssign,
    current_user: User = Depends(require_helper),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Назначение тикета на пользователя.
    
    Args:
        ticket_id: ID тикета
        assign_data: Данные для назначения
        current_user: Текущий пользователь (должен быть персоналом)
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Обновленный тикет
    """
    ticket_service = TicketService(db)
    
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    assigned_user = None
    if assign_data.assigned_to:
        from tikethet.services.user_service import UserService
        user_service = UserService(db)
        assigned_user = await user_service.get_user_by_id(assign_data.assigned_to)
        
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанный пользователь не найден"
            )
        
        if not ticket.can_be_assigned_to(assigned_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не может быть назначен на этот тикет"
            )
    
    # Назначаем тикет
    ticket = await ticket_service.assign_ticket(ticket, assigned_user)
    
    # Загружаем связанные объекты для ответа
    ticket = await ticket_service.get_ticket_by_id(ticket.id)
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        assigned_user=ticket.assigned_user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.post("/{ticket_id}/close", response_model=TicketResponse)
async def close_ticket(
    ticket_id: uuid.UUID,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Закрытие тикета.
    
    Args:
        ticket_id: ID тикета
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Закрытый тикет
    """
    ticket_service = TicketService(db)
    
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    # Проверяем права на закрытие
    if not ticket.can_be_edited_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для закрытия тикета"
        )
    
    # Закрываем тикет
    ticket = await ticket_service.close_ticket(ticket)
    
    # Загружаем связанные объекты для ответа
    ticket = await ticket_service.get_ticket_by_id(ticket.id)
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        assigned_user=ticket.assigned_user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.post("/{ticket_id}/reopen", response_model=TicketResponse)
async def reopen_ticket(
    ticket_id: uuid.UUID,
    current_user: User = Depends(require_helper),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Повторное открытие тикета.
    
    Args:
        ticket_id: ID тикета
        current_user: Текущий пользователь (должен быть персоналом)
        db: Сессия базы данных
        
    Returns:
        TicketResponse: Открытый тикет
    """
    ticket_service = TicketService(db)
    
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    # Открываем тикет заново
    ticket = await ticket_service.reopen_ticket(ticket)
    
    # Загружаем связанные объекты для ответа
    ticket = await ticket_service.get_ticket_by_id(ticket.id)
    
    return TicketResponse(
        id=ticket.id,
        title=ticket.title,
        description=ticket.description,
        category_id=ticket.category_id,
        priority=ticket.priority,
        user_id=ticket.user_id,
        assigned_to=ticket.assigned_to,
        status=ticket.status,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
        closed_at=ticket.closed_at,
        user=ticket.user,
        assigned_user=ticket.assigned_user,
        category=ticket.category,
        is_active=ticket.is_active,
        is_assigned=ticket.is_assigned,
        display_title=ticket.display_title,
        short_description=ticket.short_description
    )


@router.get("/stats/overview")
async def get_tickets_statistics(
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение статистики по тикетам.
    
    Args:
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        dict: Статистика по тикетам
    """
    ticket_service = TicketService(db)
    
    stats = await ticket_service.get_tickets_statistics(current_user)
    
    return {
        "success": True,
        "data": stats
    }