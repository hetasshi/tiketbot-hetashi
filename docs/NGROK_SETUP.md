# 🚀 Настройка ngrok для TiketHet

## 📋 Что такое ngrok и зачем нужен?

**ngrok** создает безопасный туннель между вашим localhost и публичным HTTPS URL. Это необходимо для Telegram Mini App, так как:

- Telegram требует HTTPS для Mini App
- Ваш сервер работает на `localhost:8000` (недоступен извне)
- ngrok предоставляет публичный URL типа `https://abc123.ngrok.io`

---

## 🔧 Установка ngrok на Windows

### Способ 1: Microsoft Store (Рекомендуется)
1. Откройте Microsoft Store
2. Найдите "ngrok" 
3. Нажмите "Установить"
4. После установки ngrok будет доступен из командной строки

### Способ 2: Скачать с официального сайта
1. Перейдите на https://ngrok.com/download
2. Скачайте ngrok для Windows (64-bit)
3. Распакуйте архив в любую папку (например, `C:\ngrok\`)
4. Добавьте путь к ngrok в переменную PATH:
   - Win + R → `sysdm.cpl` → "Переменные среды"
   - Системные переменные → PATH → Изменить
   - Добавить путь к папке с ngrok

### Способ 3: Winget (если установлен)
```cmd
winget install --id=ngrok.ngrok -e
```

---

## 🔑 Регистрация и получение токена

1. **Создать аккаунт:**
   - Перейдите на https://ngrok.com/
   - Нажмите "Sign up" и зарегистрируйтесь
   - Можно через GitHub, Google или email

2. **Получить authtoken:**
   - После входа перейдите в Dashboard
   - В разделе "Your Authtoken" скопируйте токен
   - Токен выглядит примерно так: `2HdxQW1X8eF9jK3L4mN5oP6qR7sT8uV9wX0yZ1`

3. **Настроить токен:**
   ```cmd
   ngrok config add-authtoken ВАШ_ТОКЕН_ЗДЕСЬ
   ```

---

## 🚀 Запуск ngrok туннеля

### Основная команда для TiketHet:
```cmd
ngrok http 8000
```

### Это создаст туннель на порт 8000 где работает WebSocket сервер

**Вывод будет примерно такой:**
```
ngrok                                                                                                               
                                                                                                                    
Visit http://localhost:4040 for advanced tunneling features                                                        
                                                                                                                    
Session Status                online                                                                               
Account                       ваш_email@example.com (Plan: Free)                                                    
Version                       3.5.0                                                                                
Region                        United States (us)                                                                   
Latency                       45ms                                                                                 
Web Interface                 http://127.0.0.1:4040                                                               
Forwarding                    https://abc123def456.ngrok.io -> http://localhost:8000                             
Forwarding                    http://abc123def456.ngrok.io -> http://localhost:8000                              
                                                                                                                    
Connections                   ttl     opn     rt1     rt5     p50     p90                                         
                             0       0       0.00    0.00    0.00    0.00   
```

**Важно:** Скопируйте HTTPS URL (например: `https://abc123def456.ngrok.io`)

---

## ⚙️ Обновление конфигурации TiketHet

После получения ngrok URL обновите файл `.env`:

```env
# Замените строку:
FRONTEND_URL=https://yourdomain.com

# На ваш ngrok URL:
FRONTEND_URL=https://abc123def456.ngrok.io
```

**Также обновите WebSocket подключения:**

В файле `frontend/js/websocket.js` замените:
```javascript
// Старый код:
constructor(baseUrl = 'ws://127.0.0.1:8000') {

// Новый код (замените на ваш ngrok URL):
constructor(baseUrl = 'wss://abc123def456.ngrok.io') {
```

---

## 🔄 Процедура запуска

**Правильный порядок запуска:**

1. **Запустить WebSocket сервер:**
   ```cmd
   cd C:\\Users\\user\\Desktop\\tiketbot
   python websocket_server.py
   ```

2. **В новом терминале запустить ngrok:**
   ```cmd
   ngrok http 8000
   ```

3. **Скопировать HTTPS URL из ngrok**

4. **Обновить .env файл** с новым URL

5. **Перезапустить бота:**
   ```cmd
   python -m app.telegram.bot
   ```

---

## 🔍 Проверка работы

1. **Откройте Telegram бота** (@tikethet_bot)
2. **Нажмите команду** `/tickets`
3. **Должна открыться кнопка** "Открыть тикеты" 
4. **При нажатии** должен открыться Mini App с интерфейсом

**Если не работает:**
- Проверьте, что ngrok запущен
- Убедитесь, что URL в .env обновлен
- Перезапустите бота после изменений

---

## 💡 Полезные команды ngrok

```cmd
# Базовый туннель
ngrok http 8000

# С поддоменом (для платных планов)
ngrok http -subdomain=tikethet 8000

# С базовой аутентификацией
ngrok http -auth="user:password" 8000

# Туннель только HTTPS (без HTTP)
ngrok http -bind-tls=true 8000

# Проверить статус
ngrok status

# Завершить все туннели
ngrok kill
```

---

## 🆓 Ограничения бесплатного плана

**Бесплатный план ngrok включает:**
- ✅ 3 туннеля одновременно  
- ✅ HTTPS/HTTP поддержка
- ✅ Базовая статистика
- ❌ Постоянные URL (меняются при перезапуске)
- ❌ Кастомные поддомены
- ❌ Расширенная статистика

**Для production рекомендуется:**
- Платный план ngrok ($8-20/месяц)
- Или VPS с собственным доменом и SSL

---

## 🛠️ Альтернативы ngrok

Если ngrok не подходит, можно использовать:

1. **Cloudflare Tunnel** (бесплатно)
2. **Serveo** (бесплатно) 
3. **LocalTunnel** (через npm)
4. **Pagekite** 
5. **Собственный VPS** с доменом

---

## ⚠️ Важные замечания

- **URL меняется** при каждом перезапуске ngrok
- **Всегда обновляйте** .env файл с новым URL
- **Перезапускайте бота** после изменения URL
- **Не коммитьте** ngrok URL в git (это временные адреса)

---

*Инструкция создана для проекта TiketHet*