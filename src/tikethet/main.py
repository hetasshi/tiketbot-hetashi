"""
Основное приложение Telegram Ticket Bot.

FastAPI приложение для управления системой поддержки через Telegram Mini App.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.config import get_settings


# Инициализация настроек
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    
    # Startup
    print(f"Starting {settings.app_name} v{settings.version}")
    
    # Создание необходимых директорий
    upload_path = Path(settings.upload_path)
    upload_path.mkdir(parents=True, exist_ok=True)
    
    log_path = Path(settings.log_file).parent
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Настройка логирования
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(settings.log_file),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"Application started in {settings.environment} mode")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down")
    print("Application shutting down")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Профессиональная система тикетов поддержки для Telegram с Mini App интерфейсом",
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)


# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins + [settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Middleware для безопасности
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)


# Статические файлы
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Frontend файлы
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory="frontend"), name="frontend")


# Uploads
uploads_path = Path(settings.upload_path)
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=settings.upload_path), name="uploads")


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """Проверка состояния системы."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "debug": settings.debug
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """Корневой endpoint."""
    return {
        "message": f"Добро пожаловать в {settings.app_name}!",
        "version": settings.version,
        "docs_url": "/docs" if settings.debug else None,
        "health_check": "/health"
    }


# Обработчик ошибок
@app.exception_handler(500)
async def internal_server_error(request: Request, exc: Exception):
    """Обработчик внутренних ошибок сервера."""
    logger = logging.getLogger(__name__)
    logger.error(f"Internal server error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Произошла внутренняя ошибка сервера" if not settings.debug else str(exc)
        }
    )


# API роуты
from app.api.v1 import auth, tickets, categories, messages
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(tickets.router, prefix="/api/v1/tickets", tags=["tickets"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(messages.router, prefix="/api/v1/tickets", tags=["messages"])


if __name__ == "__main__":
    """Запуск приложения для разработки."""
    print(f"Starting {settings.app_name} on {settings.host}:{settings.port}")
    print(f"Debug mode: {settings.debug}")
    print(f"Documentation available at: http://{settings.host}:{settings.port}/docs")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        access_log=settings.debug,
        log_level=settings.log_level.lower()
    )