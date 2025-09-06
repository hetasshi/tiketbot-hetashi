# 📡 API Документация

Полная документация REST API для Telegram Ticket Bot системы.

## 🔗 Базовый URL

```
https://api.yourbot.com/api/v1
```

## 🔐 Аутентификация

Все API endpoints (кроме авторизации) требуют JWT токен в заголовке:

```http
Authorization: Bearer <jwt_token>
```

---

## 🔑 Авторизация

### POST /auth/telegram
Авторизация пользователя через Telegram WebApp.

**Параметры:**
```json
{
  "initData": "string",  // Telegram WebApp initData
  "hash": "string"       // HMAC-SHA256 подпись
}
```

**Ответ:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 604800,
  "user": {
    "id": "uuid",
    "telegram_id": 123456789,
    "username": "john_doe",
    "first_name": "John",
    "role": "USER",
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

### GET /auth/me
Получение информации о текущем пользователе.

**Ответ:**
```json
{
  "id": "uuid",
  "telegram_id": 123456789,
  "username": "john_doe",
  "first_name": "John",
  "last_name": "Doe",
  "role": "USER",
  "is_active": true,
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z"
}
```

### PUT /auth/profile
Обновление профиля пользователя.

**Параметры:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "username": "john_doe"
}
```

---

## 🎫 Тикеты

### GET /tickets
Получение списка тикетов с фильтрацией.

**Query параметры:**
- `status` - Статус тикета (OPEN, IN_PROGRESS, WAITING_RESPONSE, RESOLVED, CLOSED)
- `category_id` - ID категории
- `priority` - Приоритет (LOW, NORMAL, HIGH, CRITICAL)
- `assigned_to` - ID назначенного пользователя
- `page` - Номер страницы (по умолчанию 1)
- `size` - Размер страницы (по умолчанию 20)

**Ответ:**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Проблема с оплатой",
      "description": "Не могу оплатить подписку",
      "status": "OPEN",
      "priority": "HIGH",
      "category": {
        "id": "uuid",
        "name": "Оплата и подписка",
        "icon": "💳"
      },
      "user": {
        "id": "uuid",
        "first_name": "John",
        "username": "john_doe"
      },
      "assigned_to": null,
      "created_at": "2024-01-01T10:00:00Z",
      "updated_at": "2024-01-01T10:00:00Z",
      "messages_count": 3,
      "last_message_at": "2024-01-01T11:00:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "size": 20,
  "pages": 3
}
```

### POST /tickets
Создание нового тикета.

**Параметры:**
```json
{
  "title": "Проблема с оплатой",
  "description": "Подробное описание проблемы...",
  "category_id": "uuid",
  "priority": "HIGH"
}
```

**Ответ:**
```json
{
  "id": "uuid",
  "title": "Проблема с оплатой",
  "description": "Подробное описание проблемы...",
  "status": "OPEN",
  "priority": "HIGH",
  "category_id": "uuid",
  "user_id": "uuid",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### GET /tickets/{id}
Получение детальной информации о тикете.

**Ответ:**
```json
{
  "id": "uuid",
  "title": "Проблема с оплатой",
  "description": "Подробное описание проблемы...",
  "status": "OPEN",
  "priority": "HIGH",
  "category": {
    "id": "uuid",
    "name": "Оплата и подписка",
    "icon": "💳",
    "color": "#ff6b6b"
  },
  "user": {
    "id": "uuid",
    "telegram_id": 123456789,
    "first_name": "John",
    "username": "john_doe"
  },
  "assigned_to": {
    "id": "uuid",
    "first_name": "Support",
    "role": "HELPER"
  },
  "created_at": "2024-01-01T10:00:00Z",
  "updated_at": "2024-01-01T12:00:00Z",
  "closed_at": null
}
```

### PUT /tickets/{id}
Обновление тикета.

**Параметры:**
```json
{
  "title": "Обновленный заголовок",
  "status": "IN_PROGRESS",
  "priority": "NORMAL",
  "assigned_to": "uuid"
}
```

### DELETE /tickets/{id}
Удаление тикета (только для админов).

**Ответ:**
```json
{
  "message": "Тикет успешно удален"
}
```

---

## 💬 Сообщения

### GET /tickets/{ticket_id}/messages
Получение истории сообщений тикета.

**Query параметры:**
- `page` - Номер страницы (по умолчанию 1)
- `size` - Размер страницы (по умолчанию 50)

**Ответ:**
```json
{
  "items": [
    {
      "id": "uuid",
      "content": "Здравствуйте! У меня проблема с оплатой...",
      "user": {
        "id": "uuid",
        "first_name": "John",
        "role": "USER"
      },
      "attachments": [
        {
          "id": "uuid",
          "filename": "screenshot.png",
          "size": 156789,
          "content_type": "image/png",
          "url": "/uploads/files/screenshot.png"
        }
      ],
      "is_internal": false,
      "created_at": "2024-01-01T10:00:00Z"
    }
  ],
  "total": 5,
  "page": 1,
  "size": 50
}
```

### POST /tickets/{ticket_id}/messages
Добавление сообщения в тикет.

**Параметры:**
```json
{
  "content": "Текст сообщения",
  "is_internal": false,  // true для внутренних заметок персонала
  "attachments": ["file_uuid_1", "file_uuid_2"]
}
```

**Ответ:**
```json
{
  "id": "uuid",
  "content": "Текст сообщения",
  "user_id": "uuid",
  "ticket_id": "uuid",
  "is_internal": false,
  "created_at": "2024-01-01T10:30:00Z"
}
```

---

## 📁 Файлы

### POST /files/upload
Загрузка файла.

**Параметры:** multipart/form-data
- `file` - Файл для загрузки

**Ответ:**
```json
{
  "id": "uuid",
  "filename": "document.pdf",
  "size": 1024567,
  "content_type": "application/pdf",
  "url": "/uploads/files/document.pdf",
  "created_at": "2024-01-01T10:00:00Z"
}
```

### GET /files/{id}
Скачивание файла.

**Ответ:** Бинарные данные файла

---

## 🏷️ Категории

### GET /categories
Получение списка категорий тикетов.

**Ответ:**
```json
[
  {
    "id": "uuid",
    "name": "Оплата и подписка",
    "description": "Вопросы по оплате, возврату средств, продлению подписки",
    "icon": "💳",
    "color": "#ff6b6b",
    "is_active": true,
    "sort_order": 1
  },
  {
    "id": "uuid",
    "name": "Технические проблемы",
    "description": "Ошибки, краши, проблемы с установкой",
    "icon": "🔧",
    "color": "#4ecdc4",
    "is_active": true,
    "sort_order": 2
  }
]
```

### POST /categories
Создание новой категории (только для админов).

**Параметры:**
```json
{
  "name": "Новая категория",
  "description": "Описание категории",
  "icon": "🆕",
  "color": "#45b7d1",
  "sort_order": 10
}
```

### PUT /categories/{id}
Обновление категории (только для админов).

### DELETE /categories/{id}
Удаление категории (только для админов).

---

## 👥 Пользователи

### GET /users
Получение списка пользователей (только для модераторов+).

**Query параметры:**
- `role` - Фильтр по роли
- `is_active` - Фильтр по активности
- `search` - Поиск по имени/username
- `page`, `size` - Пагинация

**Ответ:**
```json
{
  "items": [
    {
      "id": "uuid",
      "telegram_id": 123456789,
      "username": "john_doe",
      "first_name": "John",
      "role": "USER",
      "is_active": true,
      "created_at": "2024-01-01T10:00:00Z",
      "tickets_count": 5,
      "last_activity": "2024-01-01T15:00:00Z"
    }
  ],
  "total": 100,
  "page": 1,
  "size": 20
}
```

### PUT /users/{id}/role
Изменение роли пользователя (только для админов).

**Параметры:**
```json
{
  "role": "HELPER"
}
```

### PUT /users/{id}/status
Блокировка/разблокировка пользователя (только для админов).

**Параметры:**
```json
{
  "is_active": false
}
```

---

## 📊 Статистика

### GET /statistics/dashboard
Общая статистика для дашборда.

**Ответ:**
```json
{
  "tickets": {
    "total": 150,
    "open": 25,
    "in_progress": 15,
    "resolved": 8,
    "closed": 102
  },
  "response_time": {
    "average_hours": 4.5,
    "median_hours": 2.1
  },
  "categories": [
    {
      "name": "Оплата и подписка",
      "count": 45,
      "percentage": 30
    }
  ],
  "helpers": [
    {
      "user": {
        "first_name": "Support Agent",
        "role": "HELPER"
      },
      "tickets_handled": 25,
      "avg_response_time": 3.2
    }
  ]
}
```

### GET /statistics/tickets
Подробная статистика по тикетам.

**Query параметры:**
- `from_date` - Дата начала периода
- `to_date` - Дата окончания периода
- `category_id` - Фильтр по категории

---

## ❌ Коды ошибок

| Код | Описание |
|-----|----------|
| 400 | Некорректный запрос |
| 401 | Не авторизован |
| 403 | Доступ запрещен |
| 404 | Ресурс не найден |
| 422 | Ошибка валидации данных |
| 429 | Превышен лимит запросов |
| 500 | Внутренняя ошибка сервера |

**Пример ошибки:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Некорректные данные",
    "details": [
      {
        "field": "title",
        "message": "Заголовок обязателен"
      }
    ]
  }
}
```

---

## 🔌 WebSocket API

### Подключение
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/tickets/{ticket_id}?token={jwt_token}');
```

### События

**Новое сообщение:**
```json
{
  "type": "new_message",
  "data": {
    "id": "uuid",
    "content": "Новое сообщение",
    "user": {...},
    "created_at": "2024-01-01T10:30:00Z"
  }
}
```

**Изменение статуса:**
```json
{
  "type": "status_changed",
  "data": {
    "ticket_id": "uuid",
    "old_status": "OPEN",
    "new_status": "IN_PROGRESS",
    "changed_by": {...}
  }
}
```

**Пользователь печатает:**
```json
{
  "type": "typing",
  "data": {
    "user_id": "uuid",
    "is_typing": true
  }
}
```