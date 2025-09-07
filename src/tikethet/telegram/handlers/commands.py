"""
Базовые команды Telegram бота.
"""

import logging
from typing import Optional

from aiogram import Dispatcher, Router, html
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import WebAppInfo

from app.config import get_settings

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработчик команды /start.
    
    Приветствует пользователя и предлагает основные действия.
    """
    user = message.from_user
    if not user:
        return
    
    settings = get_settings()
    
    # Создаем клавиатуру с основными действиями
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть тикеты",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/tickets")
                )
            ],
            [
                InlineKeyboardButton(
                    text="Создать тикет поддержки",
                    callback_data="create_ticket"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Справка",
                    callback_data="help"
                )
            ]
        ]
    )
    
    welcome_text = f"""
Добро пожаловать в {html.bold(settings.app_name)}, {html.bold(user.full_name)}!

Это профессиональная система тикетов поддержки с удобным Mini App интерфейсом.

Выберите действие:
"""
    
    await message.answer(
        text=welcome_text,
        reply_markup=keyboard
    )


@router.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    Обработчик команды /help.
    
    Показывает справку по использованию бота.
    """
    help_text = f"""
{html.bold("Справка по использованию бота")}

{html.bold("Основные команды:")}
/start - Начать работу с ботом
/help - Показать эту справку
/tickets - Открыть Mini App с тикетами
/support - Создать новый тикет поддержки
/status - Показать статус активных тикетов

{html.bold("Как работать с тикетами:")}
1. Откройте Mini App через команду /tickets
2. Создавайте новые тикеты с описанием проблемы
3. Следите за статусом в режиме реального времени
4. Общайтесь с поддержкой через чат в тикете

{html.bold("Возможности системы:")}
• Создание и управление тикетами
• Чат с поддержкой в реальном времени
• Прикрепление файлов и изображений
• Категоризация по типам проблем
• Уведомления об изменениях

{html.bold("Нужна помощь?")}
Используйте /support для создания тикета техподдержки.
"""
    
    await message.answer(text=help_text)


@router.message(Command("tickets"))
async def command_tickets_handler(message: Message) -> None:
    """
    Обработчик команды /tickets.
    
    Открывает Mini App с интерфейсом тикетов.
    """
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть тикеты",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/tickets")
                )
            ]
        ]
    )
    
    await message.answer(
        text="Нажмите кнопку ниже, чтобы открыть интерфейс тикетов:",
        reply_markup=keyboard
    )


@router.message(Command("support"))
async def command_support_handler(message: Message) -> None:
    """
    Обработчик команды /support.
    
    Запускает процесс создания тикета поддержки.
    """
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Создать тикет",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/create-ticket")
                )
            ],
            [
                InlineKeyboardButton(
                    text="Быстрое обращение",
                    callback_data="quick_support"
                )
            ]
        ]
    )
    
    await message.answer(
        text="Выберите способ создания тикета поддержки:",
        reply_markup=keyboard
    )


@router.message(Command("status"))
async def command_status_handler(message: Message) -> None:
    """
    Обработчик команды /status.
    
    Показывает краткий статус активных тикетов пользователя.
    """
    user = message.from_user
    if not user:
        return
    
    # TODO: Интеграция с API для получения статуса тикетов
    # Пока что заглушка
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Подробный просмотр",
                    callback_data="view_tickets_detailed"
                )
            ]
        ]
    )
    
    status_text = f"""
{html.bold("Статус ваших тикетов")}

{html.code("Активные тикеты:")} Загружается...
{html.code("В ожидании ответа:")} Загружается...
{html.code("Решенные сегодня:")} Загружается...

Для подробного просмотра откройте Mini App.
"""
    
    await message.answer(
        text=status_text,
        reply_markup=keyboard
    )


def register_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех handlers команд.
    
    Args:
        dp: Dispatcher для регистрации handlers
    """
    dp.include_router(router)
    logger.info("Handlers команд зарегистрированы")