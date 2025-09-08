# 📦 Инструкция по установке

Подробное руководство по установке и настройке TiketHet системы.

## 🔧 Системные требования

### Минимальные требования
- **OS:** Linux Ubuntu 20.04+ / Windows 10+ / macOS 10.15+
- **Python:** 3.13+
- **RAM:** 2GB (рекомендуется 4GB+)
- **Storage:** 10GB свободного места (рекомендуется SSD)
- **Network:** Стабильное интернет-соединение

### Необходимое ПО
- **PostgreSQL:** 14+
- **Redis:** 6+
- **Git:** для клонирования репозитория
- **Docker:** (опционально, для простой установки)

## 🚀 Способы установки

### Вариант 1: Docker (Рекомендуется)

#### 1.1. Установка Docker
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Windows - скачать Docker Desktop
# macOS - скачать Docker Desktop
```

#### 1.2. Клонирование и запуск
```bash
# Клонировать репозиторий
git clone https://github.com/hetasshi/tiketbot-hetashi.git
cd tiketbot-hetashi

# Настроить переменные окружения
cp .env.example .env
nano .env  # отредактировать необходимые параметры

# Запустить базы данных
docker-compose up -d postgres redis

# Дождаться готовности БД (30-60 секунд)
docker-compose logs postgres

# Применить миграции
docker-compose run --rm app alembic upgrade head

# Запустить приложение
docker-compose up -d app
```

### Вариант 2: Ручная установка

#### 2.1. Подготовка системы

**Ubuntu/Debian:**
```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3.11 python3.11-venv python3-pip git curl
sudo apt install -y postgresql-14 postgresql-contrib redis-server
sudo apt install -y nginx certbot python3-certbot-nginx  # для продакшена

# Запуск сервисов
sudo systemctl enable postgresql redis-server
sudo systemctl start postgresql redis-server
```

**CentOS/RHEL:**
```bash
# Установка Python 3.11
sudo dnf install -y python3.11 python3.11-pip git

# Установка PostgreSQL
sudo dnf install -y postgresql14-server postgresql14-contrib
sudo postgresql-setup --initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql

# Установка Redis
sudo dnf install -y redis
sudo systemctl enable redis
sudo systemctl start redis
```

**Windows:**
1. Установить Python 3.11+ с python.org
2. Установить PostgreSQL с postgresql.org
3. Установить Redis с redis.io или использовать WSL

**macOS:**
```bash
# Установка через Homebrew
brew install python@3.11 postgresql@14 redis git
brew services start postgresql@14
brew services start redis
```

#### 2.2. Настройка базы данных

```bash
# Подключение к PostgreSQL
sudo -u postgres psql

# Создание БД и пользователя
CREATE DATABASE telegram_tickets;
CREATE USER telegram_tickets WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE telegram_tickets TO telegram_tickets;
ALTER USER telegram_tickets CREATEDB;
\q
```

#### 2.3. Установка приложения

```bash
# Клонирование репозитория
git clone https://github.com/hetasshi/tiketbot-hetashi.git
cd tiketbot-hetashi

# Создание виртуального окружения
python3.11 -m venv venv

# Активация окружения
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

# Настройка переменных окружения
cp deployment/config/.env.example deployment/config/.env
```

#### 2.4. Настройка .env файла

```bash
# Откройте файл .env и настройте следующие параметры:
nano deployment/config/.env
```

**Обязательные параметры (в `deployment/config/.env`):**
```env  
# База данных
DATABASE_URL=postgresql://telegram_tickets:your_password@localhost:5432/telegram_tickets
REDIS_URL=redis://localhost:6379/0

# Telegram Bot (получить у @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz123456789

# JWT (сгенерировать: openssl rand -hex 32)
JWT_SECRET_KEY=your_super_secret_jwt_key_here_32_characters_long

# ID главного администратора
ADMIN_TELEGRAM_ID=123456789
```

#### 2.5. Применение миграций

```bash
# Применение миграций базы данных
alembic -c deployment/alembic/alembic.ini upgrade head

# Проверка подключения к БД
python -c "
from src.tikethet.database import engine
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text('SELECT version();'))
    print('Database connected:', result.fetchone()[0])
"
```

#### 2.6. Первый запуск

```bash
# Запуск веб-сервера (разработка) 
python src/servers/main.py
# ИЛИ через uvicorn:
uvicorn src.servers.main:app --reload --host 127.0.0.1 --port 8000

# В другом терминале - запуск бота
python -m src.tikethet.telegram.bot
```

## 🤖 Настройка Telegram бота

### 3.1. Создание бота

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Сохраните полученный токен в `.env` файл

### 3.2. Настройка Mini App

```bash
# Отправьте боту команды через BotFather:
/setdomain
# Укажите ваш домен: yourdomain.com

/setmenubutton
# Настройте кнопку меню для открытия Mini App
```

### 3.3. Настройка команд бота

```bash
# Отправьте BotFather:
/setcommands

# Затем отправьте список команд:
start - Начать работу с ботом
tickets - Открыть систему тикетов
help - Справка по использованию
status - Статус моих тикетов
```

## 🌐 Развертывание в продакшене

### 4.1. Настройка Nginx

```nginx
# /etc/nginx/sites-available/telegram-tickets
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /ws {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /uploads {
        alias /path/to/tiketbot-hetashi/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
# Активация конфигурации
sudo ln -s /etc/nginx/sites-available/telegram-tickets /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Установка SSL сертификата
sudo certbot --nginx -d yourdomain.com
```

### 4.2. Настройка Systemd сервисов

**Веб-сервер:**
```ini
# /etc/systemd/system/tikethet-web.service
[Unit]
Description=TiketHet Web Server
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/tiketbot-hetashi
Environment=PATH=/path/to/tiketbot-hetashi/venv/bin
ExecStart=/path/to/tiketbot-hetashi/venv/bin/gunicorn src.servers.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

**Telegram бот:**
```ini
# /etc/systemd/system/tikethet-bot.service
[Unit]
Description=TiketHet Bot
After=network.target postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/tiketbot-hetashi
Environment=PATH=/path/to/tiketbot-hetashi/venv/bin
ExecStart=/path/to/tiketbot-hetashi/venv/bin/python -m src.tikethet.telegram.bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
# Запуск сервисов
sudo systemctl daemon-reload
sudo systemctl enable tikethet-web tikethet-bot
sudo systemctl start tikethet-web tikethet-bot

# Проверка статуса  
sudo systemctl status tikethet-web
sudo systemctl status tikethet-bot
```

## 🛠️ Дополнительные настройки

### 5.1. Настройка логирования

```bash
# Создание папки для логов
sudo mkdir -p /var/log/tikethet
sudo chown www-data:www-data /var/log/tikethet
```

### 5.2. Настройка резервного копирования

```bash
# Создание скрипта бекапа
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/tikethet"
mkdir -p "$BACKUP_DIR"

# Бекап базы данных
pg_dump -U telegram_tickets -h localhost telegram_tickets > "$BACKUP_DIR/database_$DATE.sql"

# Бекап файлов
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Удаление старых бекапов (старше 30 дней)
find "$BACKUP_DIR" -name "*.sql" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Добавление в crontab для автоматического бекапа
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/tiketbot-hetashi/backup.sh") | crontab -
```

### 5.3. Настройка мониторинга

```bash
# Установка и настройка htop для мониторинга
sudo apt install htop

# Скрипт проверки работоспособности
cat > healthcheck.sh << 'EOF'
#!/bin/bash
# Проверка веб-сервера
if ! curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "Web server is down, restarting..."
    sudo systemctl restart telegram-tickets-web
fi

# Проверка базы данных
if ! pg_isready -h localhost -p 5432 -U telegram_tickets >/dev/null 2>&1; then
    echo "Database is down!"
    # Отправить уведомление администратору
fi
EOF

chmod +x healthcheck.sh

# Добавить в crontab для проверки каждые 5 минут
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/tiketbot-hetashi/healthcheck.sh") | crontab -
```

## 🔍 Тестирование установки

### 6.1. Проверка работы API

```bash
# Проверка статуса сервера
curl http://localhost:8000/health

# Проверка документации API
curl http://localhost:8000/docs
```

### 6.2. Проверка работы бота

1. Найдите своего бота в Telegram
2. Отправьте команду `/start`
3. Убедитесь, что бот отвечает
4. Попробуйте команду `/tickets` для открытия Mini App

### 6.3. Проверка Mini App

1. Откройте Mini App через команду бота
2. Убедитесь, что интерфейс загружается
3. Попробуйте создать тестовый тикет
4. Проверьте уведомления в Telegram

## ❗ Устранение проблем

### Частые проблемы

**1. Ошибка подключения к базе данных**
```bash
# Проверка статуса PostgreSQL
sudo systemctl status postgresql

# Проверка подключения
pg_isready -h localhost -p 5432

# Проверка пользователя и БД
sudo -u postgres psql -c "\du" -c "\l"
```

**2. Бот не отвечает**
```bash
# Проверка токена бота
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"

# Проверка логов бота
sudo journalctl -u telegram-tickets-bot -f
```

**3. Mini App не загружается**
- Проверьте CORS настройки в коде
- Убедитесь, что домен правильно настроен в BotFather
- Проверьте SSL сертификат (HTTPS обязателен для Mini App)

**4. Проблемы с WebSocket**
```bash
# Проверка Nginx конфигурации для WebSocket
sudo nginx -t

# Тест WebSocket соединения
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  http://localhost:8000/ws/test
```

### Логи и отладка

```bash
# Просмотр логов приложения
sudo journalctl -u tikethet-web -f
sudo journalctl -u tikethet-bot -f

# Логи Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Логи PostgreSQL
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

## 📞 Получение поддержки

Если у вас возникли проблемы с установкой:

1. **Проверьте FAQ** в основном README.md
2. **Изучите логи** системы для диагностики
3. **Создайте Issue** в GitHub репозитории с подробным описанием проблемы
4. **Свяжитесь с поддержкой** через Telegram: [@your_support_bot](https://t.me/your_support_bot)

## ✅ Чеклист успешной установки

- [ ] PostgreSQL установлен и работает
- [ ] Redis установлен и работает  
- [ ] Python 3.11+ установлен
- [ ] Зависимости установлены
- [ ] База данных создана
- [ ] Миграции применены
- [ ] Переменные окружения настроены
- [ ] Telegram бот создан и токен добавлен
- [ ] Веб-сервер запускается без ошибок
- [ ] Бот отвечает на команды
- [ ] Mini App открывается и работает
- [ ] WebSocket соединение работает
- [ ] SSL сертификат настроен (для продакшена)
- [ ] Резервное копирование настроено
- [ ] Мониторинг работает

🎉 **Поздравляем! Ваша система тикетов готова к работе!**