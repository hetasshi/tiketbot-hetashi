"""
Упрощенный сервер для демонстрации Telegram Ticket Bot
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uvicorn

# Создание FastAPI приложения
app = FastAPI(
    title="Telegram Ticket Bot Demo",
    version="1.0.0",
    description="Demo версия системы тикетов поддержки для Telegram"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Frontend файлы
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory="frontend"), name="frontend")

# Создаем директории если их нет
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)

logs_path = Path("logs")
logs_path.mkdir(exist_ok=True)

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "Telegram Ticket Bot Demo Server running"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Добро пожаловать в Telegram Ticket Bot Demo!",
        "frontend_url": "/app/index.html",
        "api_docs": "/docs"
    }

# Mock API endpoints для демонстрации
@app.post("/api/v1/auth/telegram")
async def mock_auth():
    return {
        "access_token": "demo_token",
        "token_type": "bearer",
        "user": {
            "id": "demo-user-123",
            "telegram_id": 123456789,
            "first_name": "Demo",
            "last_name": "User",
            "username": "demo_user",
            "role": "USER"
        }
    }

@app.get("/api/v1/auth/me")
async def mock_me():
    return {
        "id": "demo-user-123",
        "telegram_id": 123456789,
        "first_name": "Demo",
        "last_name": "User",
        "username": "demo_user",
        "role": "USER",
        "is_active": True
    }

@app.get("/api/v1/tickets")
async def mock_tickets():
    return {
        "items": [
            {
                "id": "ticket-001",
                "title": "Проблема с подключением к серверу",
                "description": "Не могу подключиться к игровому серверу. Постоянно выдает ошибку таймаута.",
                "status": "OPEN",
                "priority": "HIGH",
                "category": {
                    "id": "tech-issues",
                    "name": "Технические проблемы",
                    "icon": "🔧"
                },
                "messages_count": 3,
                "created_at": "2024-12-07T10:30:00Z"
            },
            {
                "id": "ticket-002", 
                "title": "Вопрос по оплате подписки",
                "description": "Хочу продлить премиум подписку, но не понимаю как это сделать через ваш бот.",
                "status": "IN_PROGRESS",
                "priority": "NORMAL",
                "category": {
                    "id": "payment",
                    "name": "Оплата и подписки",
                    "icon": "💳"
                },
                "messages_count": 1,
                "created_at": "2024-12-06T15:20:00Z"
            },
            {
                "id": "ticket-003",
                "title": "Жалоба на игрока",
                "description": "Игрок с ником CheaterXX использует читы на сервере Survival. Прошу разобраться.",
                "status": "RESOLVED",
                "priority": "NORMAL", 
                "category": {
                    "id": "reports",
                    "name": "Жалобы на игроков",
                    "icon": "🚨"
                },
                "messages_count": 5,
                "created_at": "2024-12-05T18:45:00Z"
            }
        ],
        "total": 3,
        "page": 1,
        "size": 20,
        "pages": 1
    }

@app.get("/api/v1/categories")
async def mock_categories():
    return [
        {
            "id": "tech-issues",
            "name": "Технические проблемы",
            "description": "Проблемы с подключением, лагами, багами",
            "icon": "🔧",
            "color": "#4ECDC4",
            "is_active": True,
            "sort_order": 1
        },
        {
            "id": "payment",
            "name": "Оплата и подписки",
            "description": "Вопросы по оплате, возврату средств",
            "icon": "💳", 
            "color": "#45B7D1",
            "is_active": True,
            "sort_order": 2
        },
        {
            "id": "reports",
            "name": "Жалобы на игроков",
            "description": "Нарушения правил, читы, токсичность",
            "icon": "🚨",
            "color": "#F39C12",
            "is_active": True,
            "sort_order": 3
        }
    ]

if __name__ == "__main__":
    print("Запуск Telegram Ticket Bot Demo Server")
    print("Frontend: http://127.0.0.1:8000/app/index.html")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("Доступно по адресу: http://127.0.0.1:8000")
    
    uvicorn.run(
        "demo_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )