# 📊 Схема базы данных Telegram Ticket Bot

> **Версия схемы:** 1.0  
> **Последнее обновление:** Сентябрь 2025  
> **Совместимость:** PostgreSQL 14+, SQLAlchemy 2.x

## 📑 Оглавление

1. [🎯 Обзор системы](#-обзор-системы)
2. [📋 Основные сущности](#-основные-сущности)
3. [🔗 Связи между таблицами](#-связи-между-таблицами)
4. [📊 Диаграмма отношений](#-диаграмма-отношений)
5. [⚡ Индексы для производительности](#-индексы-для-производительности)
6. [🛡️ Правила бизнес-логики](#%EF%B8%8F-правила-бизнес-логики)
7. [🎯 Особенности реализации](#-особенности-реализации)
8. [📝 Примеры данных](#-примеры-данных)

---

## 🎯 Обзор системы

Telegram Ticket Bot использует **5 основных сущностей** для создания полноценной системы поддержки с **ролевым доступом** и **real-time уведомлениями**:

```
👥 ПОЛЬЗОВАТЕЛИ → 🎫 ТИКЕТЫ → 💬 СООБЩЕНИЯ
     ↓              ↓           ↑
🔔 УВЕДОМЛЕНИЯ ← 📂 КАТЕГОРИИ ←──┘
```

### ⚡ Краткая сводка таблиц

| Таблица | Назначение | Ключевые поля | Особенности |
|---------|------------|---------------|-------------|
| **users** | Пользователи системы | `telegram_id`, `role`, `is_active` | 5-уровневая ролевая система |
| **tickets** | Тикеты поддержки | `status`, `priority`, `user_id`, `assigned_to` | Жизненный цикл статусов |
| **messages** | Сообщения в тикетах | `ticket_id`, `user_id`, `attachments` | JSON для файлов |
| **categories** | Категории тикетов | `name`, `icon`, `color`, `sort_order` | Настраиваемый внешний вид |
| **notifications** | Системные уведомления | `user_id`, `type`, `is_read` | Real-time события |

---

## 📋 Основные сущности

> **Принципы проектирования:**  
> ✅ UUID для всех первичных ключей  
> ✅ Строгая типизация через Enum'ы  
> ✅ Timestamp'ы для аудита изменений  
> ✅ Nullable поля для гибкости  
> ✅ JSON для сложных структур данных

### 1. 👤 **USER** (Пользователи системы)
```sql
Table: users
Primary Key: id (UUID)

Поля:
├── id: UUID (Primary Key)
├── telegram_id: BigInteger (Unique) -- ID пользователя в Telegram
├── username: String(255) (nullable) -- @username в Telegram
├── first_name: String(255)         -- Имя
├── last_name: String(255) (nullable) -- Фамилия
├── role: Enum(UserRole)            -- Роль в системе
├── is_active: Boolean              -- Активен ли аккаунт
├── avatar_url: String (nullable)   -- URL аватарки пользователя
├── language_code: String(10)       -- Код языка интерфейса (по умолчанию "ru")
├── is_premium: Boolean             -- Premium статус в Telegram
├── created_at: DateTime
├── updated_at: DateTime

Роли (UserRole):
├── USER        -- Обычный пользователь (создает тикеты)
├── HELPER      -- Помощник поддержки (отвечает на тикеты)
├── MODERATOR   -- Модератор (управляет командой)
├── ADMIN       -- Администратор (полный доступ)
└── DEVELOPER   -- Разработчик (системные права)
```

### 2. 🎫 **TICKET** (Тикеты поддержки)
```sql
Table: tickets
Primary Key: id (UUID)

Поля:
├── id: UUID (Primary Key)
├── title: String(500)              -- Заголовок тикета
├── description: Text               -- Подробное описание проблемы
├── status: Enum(TicketStatus)      -- Текущий статус
├── priority: Enum(TicketPriority)  -- Приоритет решения
├── user_id: UUID (FK → users.id)   -- Автор тикета
├── assigned_to: UUID (FK → users.id, nullable) -- Назначенный сотрудник
├── category_id: UUID (FK → categories.id)      -- Категория
├── closed_at: DateTime (nullable)  -- Время закрытия
├── created_at: DateTime
├── updated_at: DateTime

Статусы (TicketStatus):
├── OPEN             -- Новый, ожидает обработки
├── IN_PROGRESS      -- Взят в работу
├── WAITING_RESPONSE -- Ожидает ответа клиента
├── RESOLVED         -- Решен, ожидает подтверждения
└── CLOSED           -- Закрыт окончательно

Приоритеты (TicketPriority):
├── LOW      -- Низкий (некритично)
├── NORMAL   -- Обычный (стандартная проблема)
├── HIGH     -- Высокий (важная проблема)
└── CRITICAL -- Критический (блокирует работу)
```

### 3. 💬 **MESSAGE** (Сообщения в тикетах)
```sql
Table: messages
Primary Key: id (UUID)

Поля:
├── id: UUID (Primary Key)
├── ticket_id: UUID (FK → tickets.id)  -- К какому тикету относится
├── user_id: UUID (FK → users.id)      -- Автор сообщения
├── content: Text                       -- Текст сообщения
├── attachments: JSON (nullable)        -- Прикрепленные файлы
├── is_internal: Boolean               -- Внутренняя заметка (не видна клиенту)
├── created_at: DateTime
├── updated_at: DateTime

Структура attachments (JSON):
[
  {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "filename": "screenshot.png",
    "size": 1024000,
    "content_type": "image/png",
    "url": "/uploads/abc123.png",
    "telegram_file_id": "BAADBAADrwADBREAAYag2eLjWjtuSbIWBA",
    "uploaded_at": "2024-01-15T11:05:00Z"
  }
]
```

### 4. 📂 **CATEGORY** (Категории тикетов)
```sql
Table: categories
Primary Key: id (UUID)

Поля:
├── id: UUID (Primary Key)
├── name: String(255) (Unique)      -- Название категории
├── description: Text (nullable)    -- Описание
├── icon: String(10)                -- Эмодзи иконка категории
├── color: String(7)                -- HEX цвет (#RRGGBB)
├── is_active: Boolean              -- Активна ли категория
├── sort_order: Integer            -- Порядок сортировки
├── created_at: DateTime
├── updated_at: DateTime

Примеры категорий по умолчанию:
├── 🔧 "Технические проблемы"     -- Проблемы с подключением, лагами
├── ⚖️ "Баны и наказания"        -- Вопросы по блокировкам, апелляции
├── 🎮 "Игровые вопросы"         -- Помощь по игровому процессу
├── 💰 "Экономика и донат"       -- Проблемы с покупками, валютой
├── 🚨 "Жалобы на игроков"       -- Нарушения правил, читерство
└── ❓ "Другое"                  -- Прочие вопросы
```

### 5. 🔔 **NOTIFICATION** (Уведомления)
```sql
Table: notifications
Primary Key: id (UUID)

Поля:
├── id: UUID (Primary Key)
├── user_id: UUID (FK → users.id)      -- Получатель уведомления
├── ticket_id: UUID (FK → tickets.id, nullable) -- Связанный тикет
├── type: Enum(NotificationType)        -- Тип уведомления
├── title: String(255)                  -- Заголовок
├── content: Text                       -- Содержание уведомления
├── is_read: Boolean                    -- Прочитано ли
├── created_at: DateTime

Типы уведомлений (NotificationType):
├── NEW_TICKET              -- Создан новый тикет
├── TICKET_ASSIGNED         -- Тикет назначен
├── TICKET_STATUS_CHANGED   -- Статус тикета изменен
├── NEW_MESSAGE            -- Новое сообщение в тикете
├── TICKET_CLOSED          -- Тикет закрыт
└── SYSTEM                 -- Системное уведомление
```

---

## 🔗 СВЯЗИ МЕЖДУ ТАБЛИЦАМИ

### One-to-Many (Один ко многим):
```
👤 User ←─── 🎫 Ticket (user_id)
  │              │
  │              └─── 💬 Message (ticket_id)
  │
  ├─── 🎫 Ticket (assigned_to) -- Назначенные тикеты
  ├─── 💬 Message (user_id)    -- Сообщения пользователя  
  └─── 🔔 Notification (user_id) -- Уведомления

📂 Category ←─── 🎫 Ticket (category_id)

🎫 Ticket ←─── 🔔 Notification (ticket_id)
```

### Foreign Key Constraints:
```sql
-- Каскадное удаление (CASCADE)
tickets.user_id → users.id (ON DELETE CASCADE)
messages.user_id → users.id (ON DELETE CASCADE)  
messages.ticket_id → tickets.id (ON DELETE CASCADE)
notifications.user_id → users.id (ON DELETE CASCADE)
notifications.ticket_id → tickets.id (ON DELETE CASCADE)

-- Установка NULL при удалении (SET NULL)
tickets.assigned_to → users.id (ON DELETE SET NULL)

-- Запрет удаления (RESTRICT)
tickets.category_id → categories.id (ON DELETE RESTRICT)
```

---

## 📊 ДИАГРАММА ОТНОШЕНИЙ

```
    👤 USER
    ├── id (PK)
    ├── telegram_id (Unique)
    ├── username
    ├── first_name
    ├── last_name
    ├── role (Enum)
    └── is_active
         │
         ├─ 1:N ──→ 🎫 TICKET
         │          ├── id (PK)
         │          ├── title
         │          ├── description  
         │          ├── status (Enum)
         │          ├── priority (Enum)
         │          ├── user_id (FK)
         │          ├── assigned_to (FK) ──┐
         │          ├── category_id (FK) ──┼──→ 📂 CATEGORY
         │          └── closed_at          │    ├── id (PK)
         │               │                 │    ├── name
         │               ├─ 1:N ──→ 💬 MESSAGE   ├── description
         │               │         ├── id (PK)   ├── icon
         │               │         ├── ticket_id (FK) ├── color
         │               │         ├── user_id (FK) ──┘ └── is_active
         │               │         ├── content
         │               │         ├── attachments (JSON)
         │               │         └── is_internal
         │               │
         │               └─ 1:N ──→ 🔔 NOTIFICATION
         │                         ├── id (PK)
         ├─ 1:N ─────────────────────→ ├── user_id (FK)
         │                         ├── ticket_id (FK)
         └─ 1:N (assigned) ────────→ ├── type (Enum)
                                   ├── title
                                   ├── content
                                   └── is_read
```

---

## ⚡ ИНДЕКСЫ ДЛЯ ПРОИЗВОДИТЕЛЬНОСТИ

```sql
-- Основные индексы для быстрого поиска
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at);
CREATE INDEX idx_messages_ticket_id ON messages(ticket_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

-- Составные индексы для сложных запросов
CREATE INDEX idx_tickets_status_priority ON tickets(status, priority);
CREATE INDEX idx_tickets_user_status ON tickets(user_id, status);
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, is_read);
```

---

## 🛡️ ПРАВИЛА БИЗНЕС-ЛОГИКИ

### 🔐 Права доступа по ролям:
- **USER**: Видит только свои тикеты и сообщения
- **HELPER**: Видит назначенные тикеты + может отвечать
- **MODERATOR**: Видит все тикеты + может назначать
- **ADMIN**: Полный доступ + управление пользователями
- **DEVELOPER**: Системные операции + резервное копирование

### 📋 Жизненный цикл тикета:
```
OPEN → IN_PROGRESS → WAITING_RESPONSE → RESOLVED → CLOSED
 ↑         ↓              ↓               ↓
 └─────────┼──────────────┼───────────────┘
           └──────────────┘
(Возможен возврат на предыдущие этапы)
```

### 🔔 Автоматические уведомления:
- Создание тикета → уведомление всем HELPER+
- Назначение тикета → уведомление назначенному
- Новое сообщение → уведомление участникам
- Изменение статуса → уведомление автору
- Закрытие тикета → уведомление автору

---

## 🎯 ОСОБЕННОСТИ РЕАЛИЗАЦИИ

### ✨ Продвинутые возможности:
1. **JSON поля** для гибкого хранения attachments
2. **Enum типы** для строгой типизации статусов
3. **UUID Primary Keys** для безопасности
4. **Каскадные удаления** для целостности данных
5. **Индексы** для высокой производительности
6. **Timestamp поля** для аудита изменений

### 🚀 Масштабируемость:
- Поддержка миллионов пользователей через BigInteger telegram_id
- Эффективные запросы через составные индексы  
- Партиционирование по дате создания (future)
- Архивирование старых тикетов (future)

### 🛠️ Интеграции:
- **Telegram Bot API** через telegram_id
- **File Upload System** через attachments JSON
- **Real-time WebSocket** для уведомлений
- **Search Engine** для полнотекстового поиска

---

## 📝 ПРИМЕРЫ ДАННЫХ

### Создание пользователя:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "telegram_id": 123456789,
  "username": "john_doe", 
  "first_name": "John",
  "last_name": "Doe",
  "role": "USER",
  "is_active": true,
  "avatar_url": "https://t.me/i/userpic/320/john_doe.jpg",
  "language_code": "en",
  "is_premium": false,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Создание тикета:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "title": "Не могу зайти на сервер",
  "description": "При попытке подключения выдает ошибку connection timeout",
  "status": "OPEN",
  "priority": "NORMAL", 
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "category_id": "550e8400-e29b-41d4-a716-446655440010",
  "created_at": "2024-01-15T11:00:00Z"
}
```

### Сообщение с вложением:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002", 
  "ticket_id": "550e8400-e29b-41d4-a716-446655440001",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "Вот скриншот ошибки:",
  "attachments": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174001",
      "filename": "error_screenshot.png",
      "size": 245760,
      "content_type": "image/png",
      "url": "/uploads/2024/01/15/abc123def456.png",
      "telegram_file_id": "BAADBAADrwADBREAAYag2eLjWjtuSbIWBA",
      "uploaded_at": "2024-01-15T11:05:00Z"
    }
  ],
  "is_internal": false,
  "created_at": "2024-01-15T11:05:00Z"
}
```

---

*📋 Эта схема обеспечивает полную функциональность системы тикетов для Telegram бота с возможностью масштабирования и расширения функций.*