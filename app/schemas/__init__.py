"""
Pydantic схемы для валидации данных API.
"""

from .user import UserCreate, UserUpdate, UserResponse
from .auth import TokenResponse, TelegramAuth
from .ticket import TicketCreate, TicketUpdate, TicketResponse, TicketListResponse
from .message import MessageCreate, MessageResponse
from .category import CategoryResponse
from .common import PaginationParams, ErrorResponse

__all__ = [
    "UserCreate",
    "UserUpdate", 
    "UserResponse",
    "TokenResponse",
    "TelegramAuth",
    "TicketCreate",
    "TicketUpdate",
    "TicketResponse",
    "TicketListResponse",
    "MessageCreate",
    "MessageResponse", 
    "CategoryResponse",
    "PaginationParams",
    "ErrorResponse"
]