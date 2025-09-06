# 🗄️ Схема базы данных

Подробная документация структуры базы данных для Telegram Ticket Bot.

## 📊 ER-диаграмма

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     USERS       │    │    TICKETS      │    │   CATEGORIES    │
│─────────────────│    │─────────────────│    │─────────────────│
│ id (UUID) PK    │    │ id (UUID) PK    │    │ id (UUID) PK    │
│ telegram_id     │<───┤ user_id FK      │    │ name            │
│ username        │    │ assigned_to FK──┼────┤ description     │
│ first_name      │    │ category_id FK──┼───>│ icon            │
│ last_name       │    │ title           │    │ color           │
│ role            │    │ description     │    │ is_active       │
│ is_active       │    │ status          │    │ sort_order      │
│ avatar_url      │    │ priority        │    │ created_at      │
│ created_at      │    │ created_at      │    │ updated_at      │
│ updated_at      │    │ updated_at      │    └─────────────────┘
└─────────────────┘    │ closed_at       │           
                       └─────────────────┘           
                              │                      
                              │                      
                              ▼                      
                    ┌─────────────────┐              
                    │    MESSAGES     │              
                    │─────────────────│              
                    │ id (UUID) PK    │              
                    │ ticket_id FK    │              
                    │ user_id FK      │              
                    │ content         │              
                    │ attachments     │              
                    │ is_internal     │              
                    │ created_at      │              
                    └─────────────────┘              
                            │                        
                            │                        
                            ▼                        
                  ┌─────────────────┐                
                  │ NOTIFICATIONS   │                
                  │─────────────────│                
                  │ id (UUID) PK    │                
                  │ user_id FK      │                
                  │ ticket_id FK    │                
                  │ type            │                
                  │ content         │                
                  │ is_read         │                
                  │ created_at      │                
                  └─────────────────┘                
```

## 📋 Структура таблиц

### 👥 users - Пользователи системы

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `telegram_id` | BIGINT | ID пользователя в Telegram | UNIQUE, NOT NULL |
| `username` | VARCHAR(255) | Username в Telegram | NULLABLE |
| `first_name` | VARCHAR(255) | Имя пользователя | NOT NULL |
| `last_name` | VARCHAR(255) | Фамилия пользователя | NULLABLE |
| `role` | ENUM | Роль пользователя | NOT NULL, DEFAULT 'USER' |
| `is_active` | BOOLEAN | Активен ли пользователь | NOT NULL, DEFAULT TRUE |
| `avatar_url` | TEXT | URL аватарки пользователя | NULLABLE |
| `language_code` | VARCHAR(10) | Язык интерфейса | DEFAULT 'ru' |
| `is_premium` | BOOLEAN | Premium статус в Telegram | DEFAULT FALSE |
| `created_at` | TIMESTAMP | Дата создания | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | NOT NULL, DEFAULT NOW() |

**Enum values для role:**
- `USER` - Обычный пользователь
- `HELPER` - Помощник поддержки  
- `MODERATOR` - Модератор
- `ADMIN` - Администратор
- `DEVELOPER` - Разработчик

**Индексы:**
```sql
CREATE UNIQUE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_active ON users(is_active);
```

### 🎫 tickets - Тикеты поддержки

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `user_id` | UUID | ID автора тикета | FK → users.id, NOT NULL |
| `assigned_to` | UUID | ID назначенного сотрудника | FK → users.id, NULLABLE |
| `category_id` | UUID | ID категории тикета | FK → categories.id, NOT NULL |
| `title` | VARCHAR(500) | Заголовок тикета | NOT NULL |
| `description` | TEXT | Описание проблемы | NOT NULL |
| `status` | ENUM | Статус тикета | NOT NULL, DEFAULT 'OPEN' |
| `priority` | ENUM | Приоритет тикета | NOT NULL, DEFAULT 'NORMAL' |
| `created_at` | TIMESTAMP | Дата создания | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | NOT NULL, DEFAULT NOW() |
| `closed_at` | TIMESTAMP | Дата закрытия | NULLABLE |

**Enum values для status:**
- `OPEN` - Открыт (новый тикет)
- `IN_PROGRESS` - В работе
- `WAITING_RESPONSE` - Ожидает ответа клиента
- `RESOLVED` - Решен
- `CLOSED` - Закрыт

**Enum values для priority:**
- `LOW` - Низкий приоритет
- `NORMAL` - Обычный приоритет  
- `HIGH` - Высокий приоритет
- `CRITICAL` - Критический приоритет

**Индексы:**
```sql
CREATE INDEX idx_tickets_user_id ON tickets(user_id);
CREATE INDEX idx_tickets_assigned_to ON tickets(assigned_to);
CREATE INDEX idx_tickets_category_id ON tickets(category_id);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_tickets_priority ON tickets(priority);
CREATE INDEX idx_tickets_created_at ON tickets(created_at DESC);
CREATE INDEX idx_tickets_status_created ON tickets(status, created_at DESC);
```

### 💬 messages - Сообщения в тикетах

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `ticket_id` | UUID | ID тикета | FK → tickets.id, NOT NULL |
| `user_id` | UUID | ID автора сообщения | FK → users.id, NOT NULL |
| `content` | TEXT | Текст сообщения | NOT NULL |
| `attachments` | JSONB | Массив вложенных файлов | DEFAULT '[]' |
| `is_internal` | BOOLEAN | Внутренняя заметка персонала | DEFAULT FALSE |
| `created_at` | TIMESTAMP | Дата создания | NOT NULL, DEFAULT NOW() |

**Структура attachments JSON:**
```json
[
  {
    "id": "uuid",
    "filename": "screenshot.png",
    "size": 156789,
    "content_type": "image/png",
    "url": "/uploads/files/screenshot.png"
  }
]
```

**Индексы:**
```sql
CREATE INDEX idx_messages_ticket_id ON messages(ticket_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_ticket_created ON messages(ticket_id, created_at DESC);
```

### 🏷️ categories - Категории тикетов

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `name` | VARCHAR(255) | Название категории | NOT NULL |
| `description` | TEXT | Описание категории | NULLABLE |
| `icon` | VARCHAR(10) | Эмодзи иконка | NOT NULL |
| `color` | VARCHAR(7) | HEX цвет категории | NOT NULL |
| `is_active` | BOOLEAN | Активна ли категория | DEFAULT TRUE |
| `sort_order` | INTEGER | Порядок сортировки | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата создания | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Дата обновления | NOT NULL, DEFAULT NOW() |

**Индексы:**
```sql
CREATE INDEX idx_categories_active ON categories(is_active);
CREATE INDEX idx_categories_sort_order ON categories(sort_order);
```

### 🔔 notifications - Уведомления

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `user_id` | UUID | ID получателя уведомления | FK → users.id, NOT NULL |
| `ticket_id` | UUID | ID связанного тикета | FK → tickets.id, NULLABLE |
| `type` | ENUM | Тип уведомления | NOT NULL |
| `title` | VARCHAR(255) | Заголовок уведомления | NOT NULL |
| `content` | TEXT | Содержание уведомления | NOT NULL |
| `is_read` | BOOLEAN | Прочитано ли уведомление | DEFAULT FALSE |
| `created_at` | TIMESTAMP | Дата создания | NOT NULL, DEFAULT NOW() |

**Enum values для type:**
- `NEW_TICKET` - Новый тикет создан
- `TICKET_ASSIGNED` - Тикет назначен
- `TICKET_STATUS_CHANGED` - Статус тикета изменен
- `NEW_MESSAGE` - Новое сообщение в тикете
- `TICKET_CLOSED` - Тикет закрыт
- `SYSTEM` - Системное уведомление

**Индексы:**
```sql
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_ticket_id ON notifications(ticket_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

## 📊 Дополнительные таблицы

### 📁 files - Файловые вложения

| Поле | Тип | Описание | Constraints |
|------|-----|----------|-------------|
| `id` | UUID | Уникальный идентификатор | PRIMARY KEY |
| `filename` | VARCHAR(255) | Имя файла | NOT NULL |
| `original_filename` | VARCHAR(255) | Оригинальное имя файла | NOT NULL |
| `size` | BIGINT | Размер файла в байтах | NOT NULL |
| `content_type` | VARCHAR(255) | MIME тип файла | NOT NULL |
| `path` | TEXT | Путь к файлу | NOT NULL |
| `url` | TEXT | URL для доступа к файлу | NOT NULL |
| `uploaded_by` | UUID | ID пользователя, загрузившего файл | FK → users.id |
| `created_at` | TIMESTAMP | Дата загрузки | NOT NULL, DEFAULT NOW() |

## 🔗 Внешние ключи

```sql
-- Тикеты
ALTER TABLE tickets ADD CONSTRAINT fk_tickets_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE tickets ADD CONSTRAINT fk_tickets_assigned_to 
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL;

ALTER TABLE tickets ADD CONSTRAINT fk_tickets_category_id 
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT;

-- Сообщения
ALTER TABLE messages ADD CONSTRAINT fk_messages_ticket_id 
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE;

ALTER TABLE messages ADD CONSTRAINT fk_messages_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Уведомления
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_user_id 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE notifications ADD CONSTRAINT fk_notifications_ticket_id 
    FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE;

-- Файлы
ALTER TABLE files ADD CONSTRAINT fk_files_uploaded_by 
    FOREIGN KEY (uploaded_by) REFERENCES users(id) ON DELETE SET NULL;
```

## 📈 Производительность

### Рекомендуемые индексы для частых запросов

```sql
-- Получение тикетов пользователя с пагинацией
CREATE INDEX idx_tickets_user_status_created ON tickets(user_id, status, created_at DESC);

-- Получение активных тикетов для персонала
CREATE INDEX idx_tickets_assigned_status ON tickets(assigned_to, status) 
    WHERE status IN ('OPEN', 'IN_PROGRESS', 'WAITING_RESPONSE');

-- Поиск тикетов по тексту (для будущих полнотекстовых поисков)
CREATE INDEX idx_tickets_title_gin ON tickets USING gin(to_tsvector('russian', title));
CREATE INDEX idx_tickets_description_gin ON tickets USING gin(to_tsvector('russian', description));

-- Статистика по категориям
CREATE INDEX idx_tickets_category_status_created ON tickets(category_id, status, created_at);
```

### Настройки PostgreSQL

```sql
-- Увеличить shared_buffers для лучшей производительности
shared_buffers = 256MB

-- Настройки для работы с JSON
shared_preload_libraries = 'pg_stat_statements'

-- Включить автовакуум для поддержания производительности
autovacuum = on
autovacuum_max_workers = 3
```

## 🔄 Миграции Alembic

### Создание первичной миграции

```bash
# Инициализация Alembic
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Initial database schema"

# Применение миграции
alembic upgrade head
```

### Пример миграции (создание таблицы users)

```python
"""Initial database schema

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Создание ENUM типов
    role_enum = postgresql.ENUM('USER', 'HELPER', 'MODERATOR', 'ADMIN', 'DEVELOPER', name='user_role')
    role_enum.create(op.get_bind())
    
    status_enum = postgresql.ENUM('OPEN', 'IN_PROGRESS', 'WAITING_RESPONSE', 'RESOLVED', 'CLOSED', name='ticket_status')
    status_enum.create(op.get_bind())
    
    priority_enum = postgresql.ENUM('LOW', 'NORMAL', 'HIGH', 'CRITICAL', name='ticket_priority')
    priority_enum.create(op.get_bind())

    # Создание таблицы users
    op.create_table('users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('first_name', sa.String(255), nullable=False),
        sa.Column('last_name', sa.String(255), nullable=True),
        sa.Column('role', role_enum, nullable=False, server_default='USER'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('language_code', sa.String(10), nullable=False, server_default='ru'),
        sa.Column('is_premium', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id')
    )
    
    # Создание индексов
    op.create_index('idx_users_telegram_id', 'users', ['telegram_id'], unique=True)
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_active', 'users', ['is_active'])

def downgrade():
    # Удаление таблицы и типов
    op.drop_table('users')
    op.execute('DROP TYPE user_role')
    op.execute('DROP TYPE ticket_status') 
    op.execute('DROP TYPE ticket_priority')
```

## 🎯 Рекомендации по использованию

1. **Используйте UUID** для всех первичных ключей для безопасности
2. **Включите партиционирование** для таблицы messages при росте данных
3. **Настройте архивирование** старых закрытых тикетов
4. **Мониторьте размер базы** и планируйте масштабирование
5. **Делайте регулярные бекапы** важных данных

## 🔧 Полезные запросы

### Статистика по тикетам
```sql
-- Количество тикетов по статусам
SELECT status, COUNT(*) as count 
FROM tickets 
GROUP BY status;

-- Среднее время решения тикетов
SELECT AVG(EXTRACT(EPOCH FROM (closed_at - created_at))/3600) as avg_hours
FROM tickets 
WHERE closed_at IS NOT NULL;
```

### Активность пользователей
```sql
-- Топ-10 самых активных пользователей
SELECT u.first_name, u.username, COUNT(t.id) as tickets_count
FROM users u
LEFT JOIN tickets t ON u.id = t.user_id
GROUP BY u.id, u.first_name, u.username
ORDER BY tickets_count DESC
LIMIT 10;
```