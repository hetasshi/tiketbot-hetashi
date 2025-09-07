"""
Сервис для работы с сообщениями в тикетах.
"""

import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.message import Message
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app.schemas.message import MessageCreate, MessageUpdate


class MessageService:
    """Сервис для управления сообщениями в тикетах."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_message_by_id(self, message_id: uuid.UUID) -> Optional[Message]:
        """
        Получение сообщения по ID.
        
        Args:
            message_id: ID сообщения
            
        Returns:
            Optional[Message]: Сообщение или None
        """
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.user))
            .where(Message.id == message_id)
        )
        return result.scalar_one_or_none()
    
    async def get_ticket_messages(
        self, 
        ticket_id: uuid.UUID, 
        user: User,
        include_internal: bool = None
    ) -> List[Message]:
        """
        Получение сообщений тикета.
        
        Args:
            ticket_id: ID тикета
            user: Пользователь, запрашивающий сообщения
            include_internal: Включать ли внутренние сообщения
            
        Returns:
            List[Message]: Список сообщений
        """
        query = select(Message).where(Message.ticket_id == ticket_id).options(
            selectinload(Message.user)
        )
        
        # Определяем, показывать ли внутренние сообщения
        if include_internal is None:
            include_internal = user.role.can_access(UserRole.HELPER)
        
        # Фильтруем внутренние сообщения для обычных пользователей
        if not include_internal:
            query = query.where(Message.is_internal == False)
        
        query = query.order_by(Message.created_at.asc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_message(
        self,
        ticket: Ticket,
        user: User,
        message_data: MessageCreate
    ) -> Message:
        """
        Создание нового сообщения в тикете.
        
        Args:
            ticket: Тикет
            user: Автор сообщения
            message_data: Данные сообщения
            
        Returns:
            Message: Созданное сообщение
        """
        # Проверяем права на создание внутренних сообщений
        is_internal = message_data.is_internal
        if is_internal and not user.role.can_access(UserRole.HELPER):
            is_internal = False
        
        message = Message(
            ticket_id=ticket.id,
            user_id=user.id,
            content=message_data.content,
            attachments=message_data.attachments,
            is_internal=is_internal
        )
        
        self.db.add(message)
        
        # Обновляем статус тикета при необходимости
        await self._update_ticket_status_on_message(ticket, user)
        
        await self.db.commit()
        await self.db.refresh(message)
        await self.db.refresh(message, ["user"])
        
        return message
    
    async def update_message(
        self,
        message: Message,
        message_data: MessageUpdate,
        user: User
    ) -> Message:
        """
        Обновление сообщения.
        
        Args:
            message: Сообщение для обновления
            message_data: Новые данные
            user: Пользователь, обновляющий сообщение
            
        Returns:
            Message: Обновленное сообщение
        """
        # Проверяем права на редактирование
        if not message.can_be_edited_by(user):
            raise PermissionError("Недостаточно прав для редактирования сообщения")
        
        update_data = message_data.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(message, field, value)
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def delete_message(self, message: Message, user: User) -> bool:
        """
        Удаление сообщения.
        
        Args:
            message: Сообщение для удаления
            user: Пользователь, удаляющий сообщение
            
        Returns:
            bool: True если удаление прошло успешно
        """
        # Проверяем права на удаление
        if not message.can_be_deleted_by(user):
            raise PermissionError("Недостаточно прав для удаления сообщения")
        
        await self.db.delete(message)
        await self.db.commit()
        
        return True
    
    async def _update_ticket_status_on_message(self, ticket: Ticket, user: User):
        """
        Обновление статуса тикета при добавлении сообщения.
        
        Args:
            ticket: Тикет
            user: Автор сообщения
        """
        from app.models.ticket import TicketStatus
        
        # Если тикет закрыт, не меняем статус
        if ticket.status == TicketStatus.CLOSED:
            return
        
        # Если сообщение от автора тикета и тикет ожидает ответа
        if (user.id == ticket.user_id and 
            ticket.status == TicketStatus.WAITING_RESPONSE):
            ticket.status = TicketStatus.IN_PROGRESS
        
        # Если сообщение от персонала и тикет открыт
        elif (user.role.can_access(UserRole.HELPER) and 
              user.id != ticket.user_id and
              ticket.status == TicketStatus.OPEN):
            ticket.status = TicketStatus.IN_PROGRESS
        
        # Если сообщение от персонала к пользователю
        elif (user.role.can_access(UserRole.HELPER) and 
              user.id != ticket.user_id and
              ticket.status == TicketStatus.IN_PROGRESS):
            ticket.status = TicketStatus.WAITING_RESPONSE
    
    async def add_attachment_to_message(
        self,
        message: Message,
        attachment_data: Dict[str, Any]
    ) -> Message:
        """
        Добавление вложения к сообщению.
        
        Args:
            message: Сообщение
            attachment_data: Данные вложения
            
        Returns:
            Message: Обновленное сообщение
        """
        if not message.attachments:
            message.attachments = []
        
        # Создаем данные вложения
        attachment = Message.create_attachment_data(
            filename=attachment_data["filename"],
            size=attachment_data["size"],
            content_type=attachment_data["content_type"],
            url=attachment_data["url"],
            file_id=attachment_data.get("telegram_file_id")
        )
        
        message.attachments.append(attachment)
        
        await self.db.commit()
        await self.db.refresh(message)
        
        return message
    
    async def get_messages_count(self, ticket_id: uuid.UUID) -> int:
        """
        Получение количества сообщений в тикете.
        
        Args:
            ticket_id: ID тикета
            
        Returns:
            int: Количество сообщений
        """
        from sqlalchemy import func
        
        result = await self.db.execute(
            select(func.count(Message.id)).where(Message.ticket_id == ticket_id)
        )
        return result.scalar()