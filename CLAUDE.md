# CLAUDE.md

Этот файл предоставляет инструкции для Claude Code (claude.ai/code) при работе с кодом в этом репозитории.

## 📋 Обзор проекта

Telegram Ticket Bot - профессиональная система тикетов поддержки для Telegram с современным Mini App интерфейсом. Проект нацелен на создание комплексной системы поддержки с коммерческим потенциалом ($500-5000 за лицензию).

**🎯 Ключевые функции:**
- **Telegram Mini App** - полноценный веб-интерфейс внутри Telegram
- **5-уровневая система ролей** (Пользователь → Помощник → Модератор → Админ → Разработчик)
- **Real-time чат** в тикетах через WebSocket
- **Файловые вложения** с обработкой и превью
- **Умная категоризация** и приоритизация тикетов
- **Аналитика и статистика** для команды поддержки

## 🏗️ Техническая архитектура

**Технологический стек:**
- **Backend:** Python 3.11+ с FastAPI фреймворком
- **База данных:** PostgreSQL 14+ с SQLAlchemy ORM + Alembic миграции
- **Telegram:** aiogram 3.x для Bot API
- **Real-time:** WebSocket для живого чата
- **Кэширование:** Redis для сессий и производительности  
- **Frontend:** HTML/CSS/JavaScript для Mini App (возможен переход на React)
- **Аутентификация:** JWT токены с валидацией Telegram WebApp
- **Контейнеризация:** Docker + docker-compose
- **CI/CD:** GitHub Actions

**Структура кодовой базы:**
```
app/
├── api/          # FastAPI REST endpoints
├── telegram/     # aiogram bot handlers  
├── websocket/    # WebSocket для real-time чата
├── services/     # Бизнес-логика (Service Layer)
├── models/       # SQLAlchemy модели БД
├── schemas/      # Pydantic схемы для валидации
├── utils/        # Утилиты и хелперы
└── main.py       # Точка входа FastAPI приложения

frontend/         # Telegram Mini App интерфейс
docs/            # Полная документация проекта
config/          # Конфигурационные файлы
docker/          # Docker конфигурация
```

## 🗄️ База данных

**Основные таблицы (PostgreSQL):**
- `users` - Пользователи Telegram с ролевым доступом и метаданными
- `tickets` - Тикеты поддержки со статусами, приоритетами и категориями  
- `messages` - Сообщения чата в тикетах с вложениями
- `categories` - Настраиваемые категории с иконками и цветами
- `notifications` - Системные уведомления для пользователей

**Подробности:** См. `docs/DATABASE.md` для полной ER-диаграммы и схемы.

## 🚀 Команды разработки

**Настройка окружения:**
```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных окружения
cp config/.env.example .env
# Редактировать .env с токенами и настройками

# Запуск инфраструктуры (PostgreSQL, Redis)
docker-compose -f docker/docker-compose.yml up -d

# Применение миграций БД
alembic -c config/alembic.ini upgrade head

# Запуск сервера разработки
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

# Запуск Telegram бота (в отдельном терминале)
python -m app.telegram.bot
```

**Полезные команды:**
```bash
# Создание новой миграции
alembic -c config/alembic.ini revision --autogenerate -m "Migration name"

# Запуск тестов
pytest

# Проверка качества кода
black . && isort . && flake8 && mypy .

# Сборка Docker образа
docker build -f docker/Dockerfile -t telegram-tickets .

# Просмотр логов контейнеров
docker-compose -f docker/docker-compose.yml logs -f
```

## 🔑 Ключевые переменные окружения

**Обязательные настройки (в `config/.env`):**
- `TELEGRAM_BOT_TOKEN` - Токен бота от @BotFather
- `DATABASE_URL` - Строка подключения PostgreSQL  
- `REDIS_URL` - Подключение к Redis для кэширования
- `JWT_SECRET_KEY` - Секретный ключ для JWT (сгенерировать: `openssl rand -hex 32`)
- `ADMIN_TELEGRAM_ID` - Telegram ID главного администратора

**Дополнительные настройки:**
- `DEBUG` - Режим разработки (True/False)
- `MAX_FILE_SIZE` - Лимит размера файлов (по умолчанию 10MB)
- `WS_MAX_CONNECTIONS` - Максимум WebSocket подключений

## 🤖 Интеграция с Telegram

**Процесс авторизации через WebApp:**
1. Пользователь открывает Mini App кнопкой в боте
2. Telegram передает `initData` с пользовательскими данными
3. Backend валидирует `initData` используя HMAC-SHA256 + bot token
4. Автоматическое создание записи пользователя при первом входе
5. Выдача JWT токена для последующих API запросов

**Команды бота:**
```
/start       - Приветствие и регистрация нового пользователя
/tickets     - Открыть Mini App с интерфейсом тикетов  
/help        - Справка по использованию системы
/status      - Быстрый статус активных тикетов
/support     - Создать тикет через упрощенную форму

# Админские команды (только для ролей Admin+)
/admin       - Открыть панель администрирования
/stats       - Показать статистику по тикетам
/role        - Назначить роль пользователю (@username ROLE)
```

## 💡 Важные заметки по разработке

### 🔐 Система ролей и безопасность
**Иерархия ролей:** Разработчик > Админ > Модератор > Помощник > Пользователь
- Каждая роль наследует права нижестоящих уровней
- Назначение ролей доступно только пользователям высшего уровня
- Проверка ролей происходит на каждом API запросе через JWT payload

### 📱 Ограничения Telegram Mini App
- Работает в WebView с ограниченным набором API
- Размер файлов ограничен Telegram (20MB через Bot API)
- Обязательна поддержка HTTPS для продакшена
- Mobile-first дизайн (90% пользователей на мобильных)
- Graceful degradation для слабых соединений

### 🛡️ Безопасность
- **Валидация на сервере:** Все данные от Mini App проверяются backend'ом
- **File uploads:** Проверка MIME-типов, размеров и вирусов
- **Rate limiting:** Лимиты на API endpoints и WebSocket подключения  
- **CORS настройка:** Разрешенные домены для Mini App
- **JWT security:** Короткие TTL, secure storage, rotation

### ⚡ Масштабируемость и производительность
- **Database indexing:** Индексы на `user_id`, `status`, `created_at`
- **Connection pooling:** Пул соединений к PostgreSQL и Redis
- **WebSocket management:** Лимиты соединений, heartbeat, cleanup
- **File storage:** Локально для dev, S3 для production
- **Caching strategy:** Redis для частых запросов, session data

## 📚 Документация проекта

**Основная документация:**
- `README.md` - Обзор проекта и быстрый старт
- `docs/TECHNICAL_REQUIREMENTS.md` - Детальное техническое задание
- `docs/ARCHITECTURE.md` - Архитектура системы с диаграммами
- `docs/DATABASE.md` - Схема БД и миграции
- `docs/API.md` - REST API документация с примерами

**Планы и стратегия:**
- `docs/ROADMAP.md` - План развития по версиям
- `docs/BUSINESS_PLAN.md` - Коммерческая стратегия и монетизация
- `docs/CHANGELOG.md` - История изменений

**Для разработчиков:**
- `docs/INSTALLATION.md` - Подробная установка и настройка
- `docs/CONTRIBUTING.md` - Руководство по участию в проекте

## 🚀 Текущий статус проекта

**Фаза:** Документация завершена, готовность к разработке MVP
**Следующий этап:** Создание базовой структуры приложения

**План реализации:**
1. **MVP (4-6 недель):** Базовый CRUD тикетов + простой Mini App + роли
2. **Enhanced (3-4 недели):** Real-time чат + уведомления + файлы
3. **Advanced (2-3 недели):** Аналитика + автоматизация + оптимизация  
4. **Commercial (3-4 недели):** White-label + монетизация + продакшн

**Коммерческий потенциал:** $100K+ ARR к концу первого года
**Целевой рынок:** Gaming communities, SMB, Discord/Telegram сообщества

## 💡 Технические решения

### 🗂️ Управление зависимостями
- **Poetry** для управления зависимостями (pyproject.toml)
- **Requirements.txt** поддерживается для совместимости
- Используй `poetry install` для установки или `pip install -r requirements.txt`

### 🏗️ Приоритеты разработки MVP
1. **Database Models** - Создать SQLAlchemy модели (users, tickets, messages, categories)
2. **Authentication** - JWT + Telegram WebApp validation
3. **Core API** - CRUD операции для тикетов
4. **Telegram Bot** - Базовые команды и Mini App интеграция
5. **Frontend** - Простой Mini App интерфейс
6. **WebSocket** - Real-time чат (можно отложить на v1.1)

### 🛠️ Спорные технические решения
- **Frontend:** React с TypeScript для Mini App интерфейса
- **File Storage:** Локальное хранение для MVP, S3 для production
- **Real-time:** Polling для MVP, WebSocket для enhanced версии
- **Auth:** Только Telegram WebApp validation, дополнительной защиты пока не нужно

## 🎯 Правила работы с проектом

### TodoWrite Usage
- Используй TodoWrite для отслеживания прогресса по задачам
- Один активный (in_progress) todo за раз
- Отмечай completed сразу после завершения
- Создавай новые todos для вновь обнаруженных задач

### Языковые требования  
- **Весь код и комментарии на английском**
- **Вся документация на русском языке** 
- **Commit messages на английском**
- **API responses и UI на русском для пользователей**

### Code Style
- Python: Black + isort + flake8 + mypy
- Docstrings в формате Google Style на русском
- FastAPI: async/await везде где возможно
- SQLAlchemy: Async sessions, declarative base