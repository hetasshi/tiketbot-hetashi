/**
 * WebSocket модуль для real-time обновлений в Telegram Ticket Bot
 * Использует лучшие практики WebSocket от FastAPI документации
 */

class WebSocketClient {
    constructor(baseUrl = null) {
        this.baseUrl = baseUrl;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000; // начальная задержка 1 секунда
        this.heartbeatInterval = null;
        
        // Колбэки для различных событий
        this.eventHandlers = {
            'connection_established': [],
            'ticket_status_changed': [],
            'new_ticket_message': [],
            'periodic_update': [],
            'error': [],
            'disconnect': []
        };
        
        this.init();
    }

    /**
     * Инициализация WebSocket подключения
     */
    async init() {
        if (!this.baseUrl) {
            await this.loadConfig();
        }
        this.connect();
    }
    
    /**
     * Загрузка конфигурации с сервера
     */
    async loadConfig() {
        try {
            const response = await fetch('/api/config');
            const config = await response.json();
            this.baseUrl = config.websocket_url;
            console.log('Загружена конфигурация WebSocket:', config);
        } catch (error) {
            console.error('Ошибка загрузки конфигурации:', error);
            // Fallback на localhost для разработки
            this.baseUrl = 'ws://127.0.0.1:8000';
        }
    }

    /**
     * Подключение к WebSocket серверу
     */
    connect() {
        try {
            console.log('Подключение к WebSocket...', `${this.baseUrl}/ws`);
            
            // Создаем WebSocket подключение
            this.socket = new WebSocket(`${this.baseUrl}/ws`);
            
            // Обработчик успешного подключения
            this.socket.onopen = (event) => {
                console.log('✅ WebSocket подключен');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                
                // Запускаем heartbeat
                this.startHeartbeat();
                
                // Подписываемся на уведомления
                this.send({
                    type: 'subscribe_notifications',
                    timestamp: new Date().toISOString()
                });
                
                // Применяем haptic feedback если доступен
                if (window.api) {
                    window.api.hapticFeedback('light');
                }
            };
            
            // Обработчик входящих сообщений
            this.socket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Ошибка парсинга WebSocket сообщения:', error);
                }
            };
            
            // Обработчик закрытия соединения
            this.socket.onclose = (event) => {
                console.log('🔌 WebSocket отключен', event.code, event.reason);
                this.isConnected = false;
                this.stopHeartbeat();
                
                // Вызываем обработчики события отключения
                this.emit('disconnect', { code: event.code, reason: event.reason });
                
                // Автоматическое переподключение
                this.scheduleReconnect();
            };
            
            // Обработчик ошибок
            this.socket.onerror = (error) => {
                console.error('❌ Ошибка WebSocket:', error);
                this.emit('error', { error: error });
            };
            
        } catch (error) {
            console.error('Ошибка создания WebSocket:', error);
            this.scheduleReconnect();
        }
    }

    /**
     * Обработка входящих сообщений
     */
    handleMessage(data) {
        console.log('📨 Получено WebSocket сообщение:', data);
        
        const messageType = data.type || 'unknown';
        
        // Обрабатываем различные типы сообщений
        switch (messageType) {
            case 'connection_established':
                console.log('🎉 Соединение установлено:', data.message);
                break;
                
            case 'ticket_status_changed':
                this.handleTicketStatusChanged(data);
                break;
                
            case 'new_ticket_message':
                this.handleNewTicketMessage(data);
                break;
                
            case 'periodic_update':
                console.log('⏰ Периодическое обновление:', data.message);
                break;
                
            case 'pong':
                console.log('🏓 Pong получен');
                break;
                
            case 'error':
                console.error('❌ Серверная ошибка:', data.message);
                break;
                
            default:
                console.log('📦 Неизвестное сообщение:', data);
        }
        
        // Вызываем зарегистрированные обработчики
        this.emit(messageType, data);
    }

    /**
     * Обработка изменения статуса тикета
     */
    handleTicketStatusChanged(data) {
        console.log(`🔄 Статус тикета ${data.ticket_id} изменен:`, 
                   `${data.old_status} → ${data.new_status}`);
        
        // Показываем уведомление пользователю
        this.showNotification(
            `Тикет "${data.ticket_title}" обновлен`,
            `Статус изменен на: ${this.getStatusText(data.new_status)}`,
            'info'
        );
        
        // Haptic feedback
        if (window.api) {
            window.api.hapticFeedback('medium');
        }
        
        // Обновляем интерфейс если тикеты загружены
        if (window.ticketApp) {
            window.ticketApp.handleTicketUpdate(data);
        }
    }

    /**
     * Обработка нового сообщения в тикете
     */
    handleNewTicketMessage(data) {
        console.log(`💬 Новое сообщение в тикете ${data.ticket_id}`);
        
        this.showNotification(
            'Новое сообщение',
            `В тикете "${data.ticket_title}"`,
            'info'
        );
        
        // Haptic feedback
        if (window.api) {
            window.api.hapticFeedback('light');
        }
    }

    /**
     * Отправка сообщения на сервер
     */
    send(message) {
        if (this.isConnected && this.socket.readyState === WebSocket.OPEN) {
            try {
                this.socket.send(JSON.stringify(message));
                console.log('📤 Отправлено WebSocket сообщение:', message);
            } catch (error) {
                console.error('Ошибка отправки WebSocket сообщения:', error);
            }
        } else {
            console.warn('⚠️ WebSocket не подключен, сообщение не отправлено:', message);
        }
    }

    /**
     * Запуск heartbeat (пинг каждые 30 секунд)
     */
    startHeartbeat() {
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected) {
                this.send({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                });
            }
        }, 30000); // 30 секунд
    }

    /**
     * Остановка heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    /**
     * Планирование переподключения с экспоненциальной задержкой
     */
    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`🔄 Попытка переподключения ${this.reconnectAttempts}/${this.maxReconnectAttempts} через ${delay}ms`);
            
            setTimeout(() => {
                this.connect();
            }, delay);
        } else {
            console.error('❌ Превышено максимальное количество попыток переподключения');
            this.showNotification(
                'Ошибка подключения',
                'Не удается установить соединение с сервером',
                'error'
            );
        }
    }

    /**
     * Регистрация обработчика события
     */
    on(eventType, handler) {
        if (!this.eventHandlers[eventType]) {
            this.eventHandlers[eventType] = [];
        }
        this.eventHandlers[eventType].push(handler);
    }

    /**
     * Удаление обработчика события
     */
    off(eventType, handler) {
        if (this.eventHandlers[eventType]) {
            const index = this.eventHandlers[eventType].indexOf(handler);
            if (index > -1) {
                this.eventHandlers[eventType].splice(index, 1);
            }
        }
    }

    /**
     * Вызов обработчиков события
     */
    emit(eventType, data) {
        if (this.eventHandlers[eventType]) {
            this.eventHandlers[eventType].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`Ошибка в обработчике события ${eventType}:`, error);
                }
            });
        }
    }

    /**
     * Показ уведомления пользователю
     */
    showNotification(title, message, type = 'info') {
        // Используем API если доступно
        if (window.api) {
            window.api.showNotification(`${title}: ${message}`, type);
            return;
        }
        
        // Fallback - системные уведомления браузера
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: message,
                icon: '/app/assets/icon.png'
            });
        }
        
        // Fallback - console
        console.log(`[${type.toUpperCase()}] ${title}: ${message}`);
    }

    /**
     * Получение текста статуса на русском языке
     */
    getStatusText(status) {
        const statusMap = {
            'OPEN': 'Открыт',
            'IN_PROGRESS': 'В работе',
            'WAITING_RESPONSE': 'Ожидает ответа',
            'RESOLVED': 'Решён',
            'CLOSED': 'Закрыт'
        };
        return statusMap[status] || status;
    }

    /**
     * Эмуляция обновления тикета для тестирования
     */
    simulateTicketUpdate(ticketId, newStatus) {
        this.send({
            type: 'ticket_update',
            ticket_id: ticketId,
            update_type: 'status_change',
            new_status: newStatus,
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Закрытие WebSocket соединения
     */
    disconnect() {
        console.log('🔌 Закрытие WebSocket соединения...');
        this.stopHeartbeat();
        
        if (this.socket) {
            this.socket.close();
        }
        
        this.isConnected = false;
        this.socket = null;
    }

    /**
     * Получение статуса подключения
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            readyState: this.socket ? this.socket.readyState : WebSocket.CLOSED,
            reconnectAttempts: this.reconnectAttempts,
            maxReconnectAttempts: this.maxReconnectAttempts
        };
    }
}

// Создаем глобальный экземпляр WebSocket клиента
window.wsClient = new WebSocketClient();

// Экспорт для модулей
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebSocketClient;
}