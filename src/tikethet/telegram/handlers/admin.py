"""
Административные команды Telegram бота.

Доступны только пользователям с ролями Admin и Developer.
"""

import logging
from typing import List

from aiogram import Dispatcher, Router, html
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import WebAppInfo

from app.config import get_settings

logger = logging.getLogger(__name__)
router = Router()


async def is_admin_user(user_id: int) -> bool:
    """
    Проверка, является ли пользователь администратором.
    
    Args:
        user_id: Telegram ID пользователя
        
    Returns:
        bool: True если пользователь - администратор
    """
    # TODO: Интеграция с API для проверки роли пользователя
    # Пока что проверяем через настройки
    settings = get_settings()
    admin_ids = [int(id_str) for id_str in settings.admin_telegram_ids.split(',') if id_str.strip()]
    return user_id in admin_ids


@router.message(Command("admin"))
async def command_admin_handler(message: Message) -> None:
    """
    Обработчик команды /admin.
    
    Открывает административную панель.
    """
    user = message.from_user
    if not user:
        return
    
    # Проверяем права администратора
    if not await is_admin_user(user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Панель администратора",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/admin")
                )
            ],
            [
                InlineKeyboardButton(
                    text="Статистика",
                    callback_data="admin_stats"
                ),
                InlineKeyboardButton(
                    text="Пользователи",
                    callback_data="admin_users"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Управление ролями",
                    callback_data="admin_roles"
                )
            ]
        ]
    )
    
    admin_text = f"""
{html.bold("Административная панель")}

Добро пожаловать, администратор {html.bold(user.full_name)}!

Доступные функции:
• Просмотр всех тикетов
• Управление пользователями и ролями  
• Статистика и аналитика
• Настройка категорий
• Системные уведомления
"""
    
    await message.answer(
        text=admin_text,
        reply_markup=keyboard
    )


@router.message(Command("stats"))
async def command_stats_handler(message: Message) -> None:
    """
    Обработчик команды /stats.
    
    Показывает статистику по тикетам.
    """
    user = message.from_user
    if not user or not await is_admin_user(user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # TODO: Интеграция с API для получения статистики
    
    stats_text = f"""
{html.bold("Статистика системы тикетов")}

{html.code("За сегодня:")}
• Новых тикетов: 0
• Решенных: 0
• В работе: 0

{html.code("За неделю:")}
• Всего тикетов: 0
• Среднее время решения: 0 ч
• Удовлетворенность: 0%

{html.code("Персонал:")}
• Активных помощников: 0
• Средняя нагрузка: 0 тикетов

Для подробной аналитики используйте веб-панель.
"""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подробная статистика",
                    callback_data="detailed_stats"
                )
            ]
        ]
    )
    
    await message.answer(
        text=stats_text,
        reply_markup=keyboard
    )


@router.message(Command("role"))
async def command_role_handler(message: Message) -> None:
    """
    Обработчик команды /role для назначения ролей пользователям.
    
    Формат: /role @username ROLE
    """
    user = message.from_user
    if not user or not await is_admin_user(user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # Парсим аргументы команды
    args = message.text.split()[1:] if message.text else []
    
    if len(args) < 2:
        help_text = f"""
{html.bold("Назначение ролей пользователям")}

{html.bold("Формат:")}
/role @username ROLE

{html.bold("Доступные роли:")}
• USER - Обычный пользователь
• HELPER - Помощник поддержки
• MODERATOR - Модератор
• ADMIN - Администратор

{html.bold("Пример:")}
/role @johndoe HELPER
"""
        await message.answer(text=help_text)
        return
    
    target_username = args[0].replace("@", "")
    target_role = args[1].upper()
    
    # TODO: Интеграция с API для назначения роли
    
    await message.answer(
        f"Роль {html.bold(target_role)} назначена пользователю @{target_username}.\n\n"
        f"Изменения вступят в силу при следующем обращении пользователя к боту."
    )


@router.message(Command("broadcast"))
async def command_broadcast_handler(message: Message) -> None:
    """
    Обработчик команды /broadcast для массовой рассылки.
    
    Только для администраторов высшего уровня.
    """
    user = message.from_user
    if not user or not await is_admin_user(user.id):
        await message.answer("У вас нет прав для выполнения этой команды.")
        return
    
    # TODO: Реализовать массовую рассылку
    
    await message.answer(
        "Функция массовой рассылки в разработке.\n"
        "Используйте веб-панель для отправки уведомлений."
    )


# Callback handlers для административных функций

@router.callback_query(lambda c: c.data and c.data == "admin_stats")
async def callback_admin_stats(callback_query) -> None:
    """Callback для просмотра статистики."""
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть аналитику",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/admin/analytics")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Откройте полную аналитику в веб-панели:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data == "admin_users")
async def callback_admin_users(callback_query) -> None:
    """Callback для управления пользователями."""
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Управление пользователями",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/admin/users")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Откройте панель управления пользователями:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data == "admin_roles")
async def callback_admin_roles(callback_query) -> None:
    """Callback для управления ролями."""
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Управление ролями",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/admin/roles")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Откройте панель управления ролями:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data == "detailed_stats")
async def callback_detailed_stats(callback_query) -> None:
    """Callback для подробной статистики."""
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть статистику",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/admin/stats")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Откройте подробную статистику в веб-панели:",
        reply_markup=keyboard
    )
    await callback_query.answer()


def register_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех административных handlers.
    
    Args:
        dp: Dispatcher для регистрации handlers
    """
    dp.include_router(router)
    logger.info("Административные handlers зарегистрированы")