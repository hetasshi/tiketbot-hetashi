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

### 🚀 Demo версия (рекомендуется для ознакомления)
```bash
# 1. Клонировать репозиторий
git clone https://github.com/hetasshi/tiketbot-hetashi.git
cd tiketbot-hetashi

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить demo сервер с WebSocket
python src/servers/websocket_server.py

# 4. Открыть в браузере
# Frontend: http://127.0.0.1:8000/app/index.html
# API Docs: http://127.0.0.1:8000/docs
```

**✅ Что работает в demo:**
- Полнофункциональный Mini App интерфейс
- WebSocket real-time уведомления  
- Все API endpoints с mock данными
- Mobile-responsive дизайн
- Connection status индикатор

### 🏗️ Production установка

#### Требования
- Python 3.13+
- PostgreSQL 14+ (для production)
- Redis 6+ (для кэширования)  
- Telegram Bot Token

#### Установка
```bash
# 1-3. Как в demo версии

# 4. Настроить переменные окружения
cp deployment/config/.env.example deployment/config/.env
# Отредактировать .env файл

# 5. Запустить базу данных (Docker)
docker-compose -f deployment/docker/docker-compose.yml up -d

# 6. Применить миграции
alembic -c deployment/alembic/alembic.ini upgrade head

# 7. Запустить production сервер
cd src && PYTHONPATH=. python servers/main.py
```

### Первый запуск

1. **Создайте бота** через [@BotFather](https://t.me/BotFather)
2. **Получите токен** и добавьте в `.env`
3. **Настройте Webhook** для Mini App
4. **Запустите проект** командами выше
5. **Запустите Telegram бота**: `cd src && PYTHONPATH=. python -m tikethet.telegram.bot`
6. **Откройте бота** в Telegram и введите `/start`

## 🎮 Использование

### Для пользователей
1. Откройте бота в Telegram
2. Нажмите `/tickets` или кнопку "Мои тикеты"
3. Создайте новый тикет через Mini App
4. Получайте уведомления о статусе

### Для поддержки
1. Получите роль Helper/Moderator от администратора
2. Используйте панель управления для работы с тикетами
3. Назначайте тикеты, меняйте статусы
4. Отслеживайте статистику работы

### Для администраторов  
1. Управляйте категориями и приоритетами
2. Настраивайте автоответы
3. Назначайте роли пользователям
4. Просматривайте детальную аналитику

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