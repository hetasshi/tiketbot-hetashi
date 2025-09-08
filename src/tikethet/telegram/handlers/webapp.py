"""
Обработчики для Telegram Web App интеграции.
"""

import json
import logging
from typing import Optional, Dict, Any

from aiogram import Dispatcher, Router
from aiogram.types import Message, CallbackQuery, WebAppData, WebAppInfo
from aiogram.filters import Filter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tikethet.config import get_settings

logger = logging.getLogger(__name__)
router = Router()


class WebAppDataFilter(Filter):
    """
    Фильтр для обработки данных от Web App.
    """
    
    async def __call__(self, message: Message) -> bool:
        return message.web_app_data is not None


@router.message(WebAppDataFilter())
async def process_web_app_data(message: Message) -> None:
    """
    Обработка данных, полученных от Web App.
    
    Args:
        message: Сообщение с данными от Web App
    """
    if not message.web_app_data:
        return
    
    try:
        # Парсим данные от Web App
        data = json.loads(message.web_app_data.data)
        logger.info(f"Received Web App data: {data}")
        
        # Обрабатываем различные типы данных
        action = data.get("action")
        
        if action == "ticket_created":
            await handle_ticket_created(message, data)
        elif action == "ticket_updated":
            await handle_ticket_updated(message, data)
        elif action == "support_request":
            await handle_support_request(message, data)
        else:
            logger.warning(f"Неизвестное действие Web App: {action}")
            await message.answer("Данные получены, но действие не распознано.")
            
    except json.JSONDecodeError:
        logger.error("Ошибка парсинга данных от Web App")
        await message.answer("Ошибка обработки данных. Попробуйте снова.")
    except Exception as e:
        logger.error(f"Ошибка обработки Web App данных: {e}")
        await message.answer("Произошла ошибка при обработке данных.")


async def handle_ticket_created(message: Message, data: Dict[str, Any]) -> None:
    """
    Обработка создания нового тикета.
    
    Args:
        message: Сообщение от пользователя
        data: Данные о созданном тикете
    """
    ticket_id = data.get("ticket_id")
    title = data.get("title", "Новый тикет")
    category = data.get("category", "Общие вопросы")
    
    success_text = f"""
Тикет создан успешно!

📋 ID: #{ticket_id}
📌 Заголовок: {title}
🏷️ Категория: {category}

Вы получите уведомления о всех изменениях статуса.
"""
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть тикет",
                    callback_data=f"open_ticket_{ticket_id}"
                )
            ]
        ]
    )
    
    await message.answer(
        text=success_text,
        reply_markup=keyboard
    )


async def handle_ticket_updated(message: Message, data: Dict[str, Any]) -> None:
    """
    Обработка обновления тикета.
    
    Args:
        message: Сообщение от пользователя
        data: Данные об обновленном тикете
    """
    ticket_id = data.get("ticket_id")
    status = data.get("status", "обновлен")
    
    update_text = f"""
Тикет #{ticket_id} {status}

Изменения сохранены в системе.
"""
    
    await message.answer(text=update_text)


async def handle_support_request(message: Message, data: Dict[str, Any]) -> None:
    """
    Обработка быстрого запроса поддержки.
    
    Args:
        message: Сообщение от пользователя
        data: Данные запроса поддержки
    """
    problem_type = data.get("problem_type", "Общий вопрос")
    description = data.get("description", "")
    
    # TODO: Интеграция с API для создания тикета
    
    success_text = f"""
Запрос поддержки отправлен!

🎯 Тип проблемы: {problem_type}
📝 Описание: {description[:100]}...

Наша команда ответит в ближайшее время.
"""
    
    await message.answer(text=success_text)


@router.callback_query(lambda c: c.data and c.data.startswith("create_ticket"))
async def callback_create_ticket(callback_query: CallbackQuery) -> None:
    """
    Callback для создания нового тикета.
    """
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть форму создания",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/create-ticket")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Нажмите кнопку ниже, чтобы открыть форму создания тикета:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("quick_support"))
async def callback_quick_support(callback_query: CallbackQuery) -> None:
    """
    Callback для быстрого создания тикета поддержки.
    """
    await callback_query.message.edit_text(
        text="""
Опишите вашу проблему в следующем сообщении.

Включите максимум деталей:
• Что произошло?
• Когда это случилось?
• Что вы пытались сделать?
• Какие сообщения об ошибках видели?

Ваше сообщение будет автоматически преобразовано в тикет поддержки.
"""
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("open_ticket_"))
async def callback_open_ticket(callback_query: CallbackQuery) -> None:
    """
    Callback для открытия конкретного тикета.
    """
    ticket_id = callback_query.data.replace("open_ticket_", "")
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть тикет",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/tickets/{ticket_id}")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text=f"Откройте тикет #{ticket_id} в Mini App:",
        reply_markup=keyboard
    )
    await callback_query.answer()


@router.callback_query(lambda c: c.data and c.data.startswith("view_tickets_detailed"))
async def callback_view_tickets_detailed(callback_query: CallbackQuery) -> None:
    """
    Callback для подробного просмотра тикетов.
    """
    settings = get_settings()
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть все тикеты",
                    web_app=WebAppInfo(url=f"{settings.frontend_url}/tickets")
                )
            ]
        ]
    )
    
    await callback_query.message.edit_text(
        text="Откройте подробный список всех ваших тикетов:",
        reply_markup=keyboard
    )
    await callback_query.answer()


def register_handlers(dp: Dispatcher) -> None:
    """
    Регистрация всех handlers Web App.
    
    Args:
        dp: Dispatcher для регистрации handlers
    """
    dp.include_router(router)
    logger.info("Web App handlers registered")