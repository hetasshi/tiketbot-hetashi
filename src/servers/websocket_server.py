"""
Улучшенный Demo сервер с WebSocket поддержкой для real-time обновлений
Использует актуальную документацию FastAPI для лучших практик
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
import json
import asyncio
from typing import List, Dict, Any
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
env_path = Path(__file__).parent.parent.parent / "deployment" / "config" / ".env"
load_dotenv(env_path)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: запуск фоновых задач
    task = asyncio.create_task(send_periodic_updates())
    print("WebSocket server started with real-time capabilities")
    yield
    # Shutdown: очистка ресурсов
    task.cancel()

# Создание FastAPI приложения
app = FastAPI(
    title="TiketHet with WebSocket",
    version="1.1.0",
    description="Demo версия с real-time обновлениями через WebSocket",
    lifespan=lifespan
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Middleware для обхода ngrok warning
@app.middleware("http")
async def add_ngrok_header(request, call_next):
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

# Frontend файлы
frontend_path = Path("frontend")
if frontend_path.exists():
    app.mount("/app", StaticFiles(directory="frontend"), name="frontend")

# Создаем директории если их нет
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)

logs_path = Path("logs")
logs_path.mkdir(exist_ok=True)


# WebSocket Connection Manager (по документации FastAPI)
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if user_id:
            self.user_connections[user_id] = websocket
        print(f"WebSocket connected. Active connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket, user_id: str = None):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id and user_id in self.user_connections:
            del self.user_connections[user_id]
        print(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.user_connections:
            websocket = self.user_connections[user_id]
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"Error sending personal message: {e}")

    async def broadcast(self, message: dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Удаляем отключенные соединения
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)


manager = ConnectionManager()

# Mock database для демонстрации
mock_tickets = [
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
        "created_at": "2024-12-07T10:30:00Z",
        "updated_at": "2024-12-07T11:15:00Z"
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
        "created_at": "2024-12-06T15:20:00Z",
        "updated_at": "2024-12-07T09:30:00Z"
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
        "created_at": "2024-12-05T18:45:00Z",
        "updated_at": "2024-12-07T14:20:00Z"
    }
]


# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "TiketHet WebSocket Server running",
        "active_connections": len(manager.active_connections),
        "features": ["WebSocket", "Real-time notifications", "Live updates"]
    }

# Configuration endpoint for frontend
@app.get("/api/config")
async def get_config():
    import os
    frontend_url = os.getenv("FRONTEND_URL", "https://localhost:8000")
    websocket_url = frontend_url.replace("https://", "wss://").replace("http://", "ws://")
    
    return {
        "frontend_url": frontend_url,
        "websocket_url": websocket_url,
        "api_base": frontend_url + "/api"
    }

# Additional routes to handle common browser requests
@app.get("/tickets")
async def tickets_redirect():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app/index.html")

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    # Return empty response to prevent 404 errors
    return Response(content="", media_type="image/x-icon")

# Root endpoint - redirect to Mini App
@app.get("/")
async def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/app/index.html")


# WebSocket endpoint (следуя документации FastAPI)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    user_id = "demo-user"  # В реальном приложении извлекается из токена
    await manager.connect(websocket, user_id)
    
    try:
        # Отправляем приветственное сообщение
        await websocket.send_json({
            "type": "connection_established",
            "message": "WebSocket соединение установлено",
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        })
        
        # Основной цикл обработки сообщений
        while True:
            try:
                # Ожидаем сообщения от клиента
                data = await websocket.receive_json()
                
                # Обрабатываем разные типы сообщений
                message_type = data.get("type", "unknown")
                
                if message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif message_type == "subscribe_notifications":
                    await websocket.send_json({
                        "type": "subscribed",
                        "message": "Подписка на уведомления активна",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                elif message_type == "ticket_update":
                    # Эмулируем обновление тикета
                    await handle_ticket_update(data, user_id)
                    
                else:
                    await websocket.send_json({
                        "type": "echo",
                        "original_message": data,
                        "timestamp": datetime.now().isoformat()
                    })
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"Error in WebSocket loop: {e}")
                await websocket.send_json({
                    "type": "error",
                    "message": f"Server error: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                })
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        manager.disconnect(websocket, user_id)


async def handle_ticket_update(data: dict, user_id: str):
    """Обработка обновлений тикетов с рассылкой уведомлений"""
    ticket_id = data.get("ticket_id")
    update_type = data.get("update_type", "status_change")
    
    # Эмулируем обновление тикета
    if ticket_id:
        # Находим тикет в mock данных
        ticket = next((t for t in mock_tickets if t["id"] == ticket_id), None)
        if ticket:
            old_status = ticket["status"]
            
            # Имитируем изменение статуса
            if update_type == "status_change":
                new_status = data.get("new_status", "IN_PROGRESS")
                ticket["status"] = new_status
                ticket["updated_at"] = datetime.now().isoformat()
                
                # Рассылаем уведомление всем подключенным пользователям
                notification = {
                    "type": "ticket_status_changed",
                    "ticket_id": ticket_id,
                    "ticket_title": ticket["title"],
                    "old_status": old_status,
                    "new_status": new_status,
                    "updated_by": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Статус тикета '{ticket['title']}' изменен на '{new_status}'"
                }
                
                await manager.broadcast(notification)
                
            elif update_type == "new_message":
                ticket["messages_count"] += 1
                ticket["updated_at"] = datetime.now().isoformat()
                
                notification = {
                    "type": "new_ticket_message",
                    "ticket_id": ticket_id,
                    "ticket_title": ticket["title"],
                    "message_author": user_id,
                    "timestamp": datetime.now().isoformat(),
                    "message": f"Новое сообщение в тикете '{ticket['title']}'"
                }
                
                await manager.broadcast(notification)


# Задача для периодической отправки обновлений
async def send_periodic_updates():
    """Отправляет периодические обновления подключенным клиентам"""
    while True:
        await asyncio.sleep(30)  # Каждые 30 секунд
        
        if manager.active_connections:
            update = {
                "type": "periodic_update",
                "timestamp": datetime.now().isoformat(),
                "active_connections": len(manager.active_connections),
                "server_status": "healthy",
                "message": "Периодическое обновление статуса"
            }
            
            await manager.broadcast(update)


# Mock API endpoints (обновленные для работы с WebSocket)
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
async def get_tickets():
    return {
        "items": mock_tickets,
        "total": len(mock_tickets),
        "page": 1,
        "size": 20,
        "pages": 1
    }

# Новый endpoint для тестирования WebSocket уведомлений
@app.post("/api/v1/tickets/{ticket_id}/update")
async def update_ticket_status(ticket_id: str, update_data: dict):
    """Endpoint для тестирования real-time обновлений тикетов"""
    
    # Эмулируем обновление через WebSocket
    await handle_ticket_update({
        "ticket_id": ticket_id,
        "update_type": "status_change",
        "new_status": update_data.get("status", "IN_PROGRESS")
    }, "admin-user")
    
    return {
        "success": True,
        "message": f"Тикет {ticket_id} обновлен",
        "timestamp": datetime.now().isoformat(),
        "broadcast_sent": True
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
    print("Starting TiketHet WebSocket Server")
    print("Frontend: http://127.0.0.1:8000/app/index.html")
    print("API Docs: http://127.0.0.1:8000/docs")
    print("WebSocket: ws://127.0.0.1:8000/ws")
    print("Available at: http://127.0.0.1:8000")
    print("Real-time updates enabled!")
    
    uvicorn.run(
        "websocket_server:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )