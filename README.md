# 🎫 TiketHet

Профессиональная система тикетов поддержки для Telegram с современным Mini App интерфейсом.

## 🚀 Особенности

### ⚡ Telegram Mini App
- **Полноценный веб-интерфейс** внутри Telegram
- **Реалтайм чат** в тикетах через WebSocket  
- **Адаптивный дизайн** для всех устройств
- **Нативная интеграция** с Telegram UI

### 👥 Система ролей
- **5-уровневая иерархия**: Пользователь → Помощник → Модератор → Админ → Разработчик
- **Гибкие права доступа** для каждой роли
- **Автоматическое назначение** при первом входе

### 🎯 Умная категоризация
- **Настраиваемые категории** тикетов
- **Приоритеты**: Низкий, Обычный, Высокий, Критический  
- **Автоматическая маршрутизация** по специалистам
- **Статистика** по категориям

### 📊 Аналитика и отчеты
- **Дашборд в реальном времени**
- **Метрики производительности** команды поддержки
- **Экспорт отчетов** в различные форматы
- **Прогнозирование нагрузки**

## 🛠️ Технический стек

- **Backend**: Python 3.13+ с FastAPI
- **База данных**: PostgreSQL + Redis
- **Telegram**: aiogram 3.x для Bot API
- **Фронтенд**: HTML/CSS/JS для Mini App
- **Real-time**: WebSocket соединения
- **ORM**: SQLAlchemy + Alembic миграции

## 📦 Быстрый старт

### 🚀 Demo версия (для тестирования)

**Запуск за 30 секунд:**
```bash
# 1. Установить зависимости
pip install fastapi uvicorn[standard] websockets

# 2. Запустить demo сервер
python src/servers/websocket_server.py

# 3. Открыть в браузере
# Frontend: http://127.0.0.1:8000/app/index.html
# API Docs: http://127.0.0.1:8000/docs
```

**✅ Что работает в demo:**
- Полнофункциональный Mini App интерфейс
- WebSocket real-time уведомления  
- Все API endpoints с mock данными
- Mobile-responsive дизайн
- Connection status индикатор

### 🤖 Telegram Bot (основной функционал)

**Простой запуск:**
```bash
# 1. Установить полные зависимости
pip install -r requirements.txt

# 2. Создать .env файл (скопировать из примера)
cp deployment/config/.env.example .env
# Добавить TELEGRAM_BOT_TOKEN в .env

# 3. Запустить бота
python run_bot.py
```

### 🏗️ Production версия (с базой данных)

**Полная установка:**
```bash
# 1-2. Как выше

# 3. Запустить PostgreSQL (Docker)
docker-compose -f deployment/docker/docker-compose.yml up -d

# 4. Применить миграции
alembic -c deployment/config/alembic.ini upgrade head

# 5. Запустить production сервер
python src/servers/main.py
```

## 🎮 Использование

### Для быстрого тестирования
1. Запустите demo сервер: `python src/servers/websocket_server.py`
2. Откройте: http://127.0.0.1:8000/app/index.html
3. Тестируйте интерфейс с mock данными

### Для реального использования в Telegram
1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен и добавьте в `.env`
3. Запустите: `python run_bot.py`
4. Настройте ngrok для публичного доступа (см. DEMO_QUICK_START.md)

### Полная настройка с базой данных
1. Установите PostgreSQL и Redis
2. Настройте connection strings в `.env`
3. Запустите миграции: `alembic upgrade head`
4. Запустите production сервер: `python src/servers/main.py`

## 📖 Документация

- [📋 Установка и настройка](docs/INSTALLATION.md)
- [🏗️ Архитектура системы](docs/ARCHITECTURE.md) 
- [🗄️ Схема базы данных](docs/DATABASE.md)
- [📡 API документация](docs/API.md)

## 🔧 API Endpoints

```http
# Авторизация
POST /api/v1/auth/telegram       # Вход через Telegram WebApp
GET  /api/v1/auth/me             # Информация о текущем пользователе

# Тикеты  
GET    /api/v1/tickets          # Список тикетов
POST   /api/v1/tickets          # Создание тикета
GET    /api/v1/tickets/{id}     # Детали тикета
PUT    /api/v1/tickets/{id}     # Обновление тикета
DELETE /api/v1/tickets/{id}     # Удаление тикета

# Сообщения
POST /api/v1/tickets/{id}/messages    # Добавить сообщение
GET  /api/v1/tickets/{id}/messages    # История сообщений

# Категории
GET  /api/v1/categories         # Список категорий
POST /api/v1/categories         # Создание категории
PUT  /api/v1/categories/{id}    # Обновление категории
```

## 🚀 Развертывание

### Docker (рекомендуется)

```bash
# Сборка образа
docker build -f deployment/docker/Dockerfile -t tikethet .

# Запуск с docker-compose
docker-compose -f deployment/docker/docker-compose.yml --profile production up -d
```

### Обычное развертывание

```bash
# Установка на production сервер
pip install -r requirements.txt
alembic -c deployment/alembic/alembic.ini upgrade head

# Запуск с Gunicorn
cd src && PYTHONPATH=. gunicorn tikethet.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## 🎯 Roadmap

- [x] **v1.0** - ✅ **MVP ЗАВЕРШЕН (100%)** - базовый функционал + WebSocket real-time
- [ ] **v1.1** - 🚀 **ГОТОВ К СТАРТУ** - ngrok интеграция и файловые вложения  
- [ ] **v1.2** - Расширенная аналитика и автоответы
- [ ] **v1.3** - Интеграции с внешними системами
- [ ] **v2.0** - White-label решение для продажи

**🎉 СТАТУС:** MVP полностью готов к демонстрации и тестированию! Требуется только ngrok для публичного HTTPS доступа.

## 💰 Лицензия и монетизация

Этот проект разработан для коммерческого использования:

- **Базовая лицензия**: $500-800 (исходный код)
- **Премиум**: $1500-2500 (код + настройка + поддержка)  
- **SaaS**: $50-150/месяц (хостинг + обслуживание)
- **Корпоративная**: $3000-5000 (полная кастомизация)

## 🤝 Вклад в проект

1. Сделайте Fork проекта
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

- **Telegram**: [@your_support_bot](https://t.me/your_support_bot)
- **Email**: support@yourproject.com
- **Документация**: [docs.yourproject.com](https://docs.yourproject.com)
- **Issues**: [GitHub Issues](https://github.com/your-username/telegram-ticket-bot/issues)

## 📄 Лицензия

Этот проект лицензирован под MIT License - подробности в файле [LICENSE](LICENSE).

---

**⭐ Поставьте звезду, если проект оказался полезным!**

🔥 **Готовы к продаже? Свяжитесь с нами для получения коммерческой лицензии!**