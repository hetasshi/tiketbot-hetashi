"""
API endpoints для аутентификации.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tikethet.database import get_db_session
from tikethet.schemas.auth import TelegramAuth, TokenResponse, LoginRequest
from tikethet.schemas.user import UserResponse
from tikethet.services.auth_service import AuthService
from tikethet.api.dependencies import AuthDependencies

router = APIRouter()


@router.post("/telegram", response_model=TokenResponse)
async def authenticate_telegram(
    auth_data: TelegramAuth,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Аутентификация пользователя через Telegram WebApp.
    
    Args:
        auth_data: Данные аутентификации от Telegram WebApp
        db: Сессия базы данных
        
    Returns:
        TokenResponse: JWT токен и данные пользователя
        
    Raises:
        HTTPException: Если данные невалидны
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, expires_at = await auth_service.authenticate_telegram_user(
            auth_data.init_data
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Ошибка аутентификации: {str(e)}"
        )
    
    # Создание ответа с пользователем
    user_response = UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        language_code=user.language_code,
        is_premium=user.is_premium,
        created_at=user.created_at,
        updated_at=user.updated_at,
        full_name=user.full_name,
        display_name=user.display_name
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=user_response
    )


@router.post("/login", response_model=TokenResponse)
async def simple_login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Простая аутентификация для тестирования (без валидации Telegram).
    
    Args:
        login_data: Данные для входа
        db: Сессия базы данных
        
    Returns:
        TokenResponse: JWT токен и данные пользователя
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, expires_at = await auth_service.authenticate_simple_login(login_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка входа: {str(e)}"
        )
    
    # Создание ответа с пользователем
    user_response = UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        is_active=user.is_active,
        avatar_url=user.avatar_url,
        language_code=user.language_code,
        is_premium=user.is_premium,
        created_at=user.created_at,
        updated_at=user.updated_at,
        full_name=user.full_name,
        display_name=user.display_name
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_at=expires_at,
        user=user_response
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(AuthDependencies.get_current_user)
):
    """
    Получение информации о текущем пользователе.
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        UserResponse: Данные пользователя
    """
    return UserResponse(
        id=current_user.id,
        telegram_id=current_user.telegram_id,
        username=current_user.username,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        is_active=current_user.is_active,
        avatar_url=current_user.avatar_url,
        language_code=current_user.language_code,
        is_premium=current_user.is_premium,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        full_name=current_user.full_name,
        display_name=current_user.display_name
    )


@router.post("/verify")
async def verify_token(
    current_user = Depends(AuthDependencies.get_current_user)
):
    """
    Проверка действительности токена.
    
    Args:
        current_user: Текущий пользователь
        
    Returns:
        dict: Статус проверки
    """
    return {
        "valid": True,
        "user_id": str(current_user.id),
        "role": current_user.role.value
    }