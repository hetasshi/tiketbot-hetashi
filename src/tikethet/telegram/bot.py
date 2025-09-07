"""
Основной Telegram бот для системы тикетов поддержки.

Использует aiogram 3.x для обработки сообщений и команд.
Интегрируется с FastAPI приложением через API.
"""

import asyncio
import logging
import sys
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from tikethet.config import get_settings
from tikethet.telegram.handlers import commands, webapp, admin

logger = logging.getLogger(__name__)


async def set_bot_commands(bot: Bot):
    """
    Установка команд бота в меню Telegram.
    """
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Справка по использованию"),
        BotCommand(command="tickets", description="Открыть Mini App тикетов"),
        BotCommand(command="support", description="Создать тикет поддержки"),
        BotCommand(command="status", description="Статус активных тикетов"),
    ]
    
    await bot.set_my_commands(commands)
    logger.info("Команды бота установлены")


async def setup_webhook(bot: Bot, settings) -> web.Application:
    """
    Настройка webhook для продакшен режима.
    
    Args:
        bot: Экземпляр бота
        settings: Настройки приложения
        
    Returns:
        web.Application: Configured aiohttp application
    """
    webhook_url = f"{settings.webhook_url}{settings.webhook_path}"
    await bot.set_webhook(
        url=webhook_url,
        secret_token=settings.webhook_secret
    )
    
    logger.info(f"Webhook установлен: {webhook_url}")
    
    # Создаем aiohttp приложение для webhook
    app = web.Application()
    
    # Создаем dispatcher
    dp = Dispatcher()
    
    # Регистрируем handlers
    commands.register_handlers(dp)
    webapp.register_handlers(dp)
    admin.register_handlers(dp)
    
    # Создаем webhook request handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.webhook_secret,
    )
    
    # Регистрируем webhook handler
    webhook_requests_handler.register(app, path=settings.webhook_path)
    
    # Настройка приложения
    setup_application(app, dp, bot=bot)
    
    return app


async def start_polling(bot: Bot, dp: Dispatcher):
    """
    Запуск бота в режиме long polling для разработки.
    
    Args:
        bot: Экземпляр бота
        dp: Dispatcher
    """
    # Регистрируем handlers
    commands.register_handlers(dp)
    webapp.register_handlers(dp)
    admin.register_handlers(dp)
    
    # Удаляем webhook если был установлен
    await bot.delete_webhook(drop_pending_updates=True)
    
    logger.info("Запуск бота в режиме polling...")
    
    # Запускаем polling
    await dp.start_polling(bot)


async def main():
    """
    Главная функция запуска бота.
    """
    # Загружаем настройки
    settings = get_settings()
    
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout
    )
    
    logger.info(f"Запуск Telegram бота {settings.app_name}")
    logger.info(f"Режим разработки: {settings.debug}")
    
    # Проверяем токен бота
    if not settings.telegram_bot_token:
        logger.error("TELEGRAM_BOT_TOKEN не установлен!")
        return
    
    # Создаем экземпляр бота
    bot = Bot(
        token=settings.telegram_bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот @{bot_info.username} успешно инициализирован")
        
        # Устанавливаем команды
        await set_bot_commands(bot)
        
        if settings.webhook_mode:
            # Webhook режим для продакшен
            logger.info("Запуск в webhook режиме")
            app = await setup_webhook(bot, settings)
            
            # Запускаем aiohttp сервер
            web.run_app(
                app,
                host=settings.webhook_host,
                port=settings.webhook_port
            )
        else:
            # Polling режим для разработки
            logger.info("Запуск в polling режиме")
            dp = Dispatcher()
            await start_polling(bot, dp)
            
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}", exc_info=True)
    finally:
        # Закрываем сессию бота
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        sys.exit(1)