# 🔧 Инструкции по тестированию TiketHet

## Исправленные проблемы

✅ **API таймаут** - Увеличен таймаут до 10 секунд
✅ **window.api.waitForConfig** - Исправлена функция ожидания конфигурации  
✅ **Мобильные задержки** - Добавлены задержки для стабильности на мобильных
✅ **ngrok конфигурация** - Исправлены fallback URL для Telegram WebApp
✅ **Глобальные переменные** - Исправлены обращения к `window.api`

## Тестирование в Telegram

### 1. Простой тест
Откройте в Telegram WebApp:
```
https://untabled-presuitably-owen.ngrok-free.app/app/test.html
```

### 2. Продвинутый тест
```
https://untabled-presuitably-owen.ngrok-free.app/app/debug-api.html
```

### 3. Основное приложение
```
https://untabled-presuitably-owen.ngrok-free.app/app/index.html
```

## Что должно работать

✅ **API конфигурация** загружается с сервера
✅ **WebSocket** подключается и получает сообщения  
✅ **Тикеты** загружаются из mock данных
✅ **Авторизация** через Telegram WebApp
✅ **Интерфейс** отображается корректно

## Диагностика проблем

### В консоли браузера должны быть логи:
```
DOM загружен, инициализируем приложение...
✅ API готов, создаем TicketApp...
API baseURL: https://untabled-presuitably-owen.ngrok-free.app/api/v1
🔧 Инициализация API начата...
✅ Конфигурация API загружена
✅ WebSocket подключен
✅ Пользователь авторизован
✅ Тикеты загружены: 3 шт.
```

### Если есть ошибки:
1. Проверьте, что сервер запущен на порту 8000
2. Проверьте, что ngrok работает
3. Откройте тестовые страницы для диагностики

## Проверка серверов

```powershell
# Проверить процессы Python
Get-Process | Where-Object {$_.ProcessName -like "*python*"}

# Проверить ngrok
Get-Process | Where-Object {$_.ProcessName -like "*ngrok*"}

# Проверить порт 8000
netstat -an | findstr ":8000"
```

## Логи и отладка

Все логи выводятся в консоль браузера. Для подробной диагностики:

1. Откройте DevTools (F12)
2. Перейдите в Console  
3. Обновите страницу
4. Проверьте логи инициализации

Если проблемы остаются, проверьте тестовые страницы `/app/test.html` и `/app/debug-api.html`.