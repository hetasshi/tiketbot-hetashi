"""
Конфигурация базы данных и сессий SQLAlchemy.
"""

from typing import AsyncGenerator
import logging

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from tikethet.config import get_settings
from tikethet.models.base import Base

# Получение настроек
settings = get_settings()

# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(
    settings.database_url_async,
    echo=settings.debug,  # Логирование SQL запросов в debug режиме
    poolclass=NullPool if settings.debug else None,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Создание фабрики сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

logger = logging.getLogger(__name__)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии базы данных в FastAPI.
    
    Yields:
        AsyncSession: Асинхронная сессия SQLAlchemy
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Создание всех таблиц в базе данных."""
    logger.info("Creating database tables...")
    
    async with engine.begin() as conn:
        # Удаление всех таблиц (только для разработки!)
        if settings.debug and settings.environment == "development":
            logger.warning("Dropping all tables (development mode)")
            await conn.run_sync(Base.metadata.drop_all)
        
        # Создание всех таблиц
        await conn.run_sync(Base.metadata.create_all)
        
    logger.info("Database tables created successfully")


async def close_db():
    """Закрытие соединений с базой данных."""
    logger.info("Closing database connections...")
    await engine.dispose()


async def check_db_connection():
    """
    Проверка соединения с базой данных.
    
    Returns:
        bool: True если соединение успешно
    """
    try:
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        logger.info("Database connection is healthy")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# Для использования в Alembic
def get_sync_url() -> str:
    """Получение синхронного URL для Alembic миграций."""
    return settings.database_url