"""
API endpoints для работы с сообщениями в тикетах.
"""

import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from tikethet.database import get_db_session
from tikethet.models.user import User
from tikethet.schemas.message import MessageCreate, MessageUpdate, MessageResponse
from tikethet.schemas.common import SuccessResponse
from tikethet.services.ticket_service import TicketService
from tikethet.services.message_service import MessageService
from tikethet.api.dependencies import require_user

router = APIRouter()


@router.get("/{ticket_id}/messages", response_model=List[MessageResponse])
async def get_ticket_messages(
    ticket_id: uuid.UUID,
    include_internal: bool = Query(None, description="Включать внутренние сообщения"),
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Получение сообщений тикета.
    
    Args:
        ticket_id: ID тикета
        include_internal: Включать ли внутренние сообщения (автоопределение по роли)
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        List[MessageResponse]: Список сообщений тикета
    """
    ticket_service = TicketService(db)
    message_service = MessageService(db)
    
    # Проверяем существование тикета и права доступа
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    if not ticket.can_be_viewed_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра сообщений тикета"
        )
    
    # Получаем сообщения
    messages = await message_service.get_ticket_messages(
        ticket_id, current_user, include_internal
    )
    
    return [
        MessageResponse(
            id=message.id,
            ticket_id=message.ticket_id,
            user_id=message.user_id,
            content=message.content,
            attachments=message.attachments,
            is_internal=message.is_internal,
            created_at=message.created_at,
            user=message.user,
            has_attachments=message.has_attachments,
            attachment_count=message.attachment_count,
            short_content=message.short_content
        )
        for message in messages
    ]


@router.post("/{ticket_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(
    ticket_id: uuid.UUID,
    message_data: MessageCreate,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Создание нового сообщения в тикете.
    
    Args:
        ticket_id: ID тикета
        message_data: Данные сообщения
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        MessageResponse: Созданное сообщение
    """
    ticket_service = TicketService(db)
    message_service = MessageService(db)
    
    # Проверяем существование тикета и права доступа
    ticket = await ticket_service.get_ticket_by_id(ticket_id, load_relations=False)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Тикет не найден"
        )
    
    if not ticket.can_be_viewed_by(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания сообщений в этом тикете"
        )
    
    # Создаем сообщение
    message = await message_service.create_message(ticket, current_user, message_data)
    
    return MessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        user_id=message.user_id,
        content=message.content,
        attachments=message.attachments,
        is_internal=message.is_internal,
        created_at=message.created_at,
        user=message.user,
        has_attachments=message.has_attachments,
        attachment_count=message.attachment_count,
        short_content=message.short_content
    )


@router.put("/messages/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: uuid.UUID,
    message_data: MessageUpdate,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Обновление сообщения.
    
    Args:
        message_id: ID сообщения
        message_data: Новые данные сообщения
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        MessageResponse: Обновленное сообщение
    """
    message_service = MessageService(db)
    
    # Получаем сообщение
    message = await message_service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )
    
    # Обновляем сообщение
    try:
        message = await message_service.update_message(message, message_data, current_user)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования сообщения"
        )
    
    return MessageResponse(
        id=message.id,
        ticket_id=message.ticket_id,
        user_id=message.user_id,
        content=message.content,
        attachments=message.attachments,
        is_internal=message.is_internal,
        created_at=message.created_at,
        user=message.user,
        has_attachments=message.has_attachments,
        attachment_count=message.attachment_count,
        short_content=message.short_content
    )


@router.delete("/messages/{message_id}", response_model=SuccessResponse)
async def delete_message(
    message_id: uuid.UUID,
    current_user: User = Depends(require_user),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Удаление сообщения.
    
    Args:
        message_id: ID сообщения
        current_user: Текущий пользователь
        db: Сессия базы данных
        
    Returns:
        SuccessResponse: Результат удаления
    """
    message_service = MessageService(db)
    
    # Получаем сообщение
    message = await message_service.get_message_by_id(message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сообщение не найдено"
        )
    
    # Удаляем сообщение
    try:
        await message_service.delete_message(message, current_user)
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления сообщения"
        )
    
    return SuccessResponse(
        success=True,
        message="Сообщение успешно удалено"
    )