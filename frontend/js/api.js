/**
 * API модуль для работы с backend Telegram Ticket Bot
 */

class API {
    constructor() {
        // Настройки API
        this.baseURL = 'http://127.0.0.1:8000/api/v1';
        this.token = null;
        
        // Инициализация при создании экземпляра
        this.init();
    }

    /**
     * Инициализация API
     */
    init() {
        // Получаем токен из localStorage если есть
        this.token = localStorage.getItem('auth_token');
        
        // Telegram WebApp инициализация
        if (window.Telegram?.WebApp) {
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
            
            // Применяем цветовую схему Telegram
            this.applyTelegramTheme();
        }
    }

    /**
     * Применение цветовой темы Telegram
     */
    applyTelegramTheme() {
        const webApp = window.Telegram.WebApp;
        if (!webApp) return;

        const root = document.documentElement;
        
        // Применяем цвета темы
        if (webApp.themeParams) {
            Object.entries(webApp.themeParams).forEach(([key, value]) => {
                if (value) {
                    root.style.setProperty(`--tg-theme-${key.replace(/_/g, '-')}`, value);
                }
            });
        }

        // Устанавливаем цвет заголовка
        webApp.setHeaderColor(webApp.themeParams.bg_color || '#ffffff');
        
        // Настраиваем главную кнопку (по умолчанию скрыта)
        webApp.MainButton.hide();
    }

    /**
     * Выполнение HTTP запроса
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };

        // Добавляем токен авторизации если есть
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            // Проверяем статус ответа
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    /**
     * Авторизация через Telegram WebApp
     */
    async authenticate() {
        const webApp = window.Telegram?.WebApp;
        
        if (!webApp || !webApp.initData) {
            throw new Error('Telegram WebApp недоступен');
        }

        try {
            const response = await this.request('/auth/telegram', {
                method: 'POST',
                body: JSON.stringify({
                    initData: webApp.initData,
                    hash: webApp.initDataUnsafe?.hash || ''
                })
            });

            // Сохраняем токен
            this.token = response.access_token;
            localStorage.setItem('auth_token', this.token);
            localStorage.setItem('user_data', JSON.stringify(response.user));

            return response;
        } catch (error) {
            console.error('Authentication failed:', error);
            throw new Error('Ошибка авторизации');
        }
    }

    /**
     * Получение информации о текущем пользователе
     */
    async getCurrentUser() {
        return await this.request('/auth/me');
    }

    /**
     * Получение списка тикетов
     */
    async getTickets(params = {}) {
        const searchParams = new URLSearchParams();
        
        // Добавляем параметры фильтрации
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                searchParams.append(key, value);
            }
        });

        const query = searchParams.toString();
        const endpoint = `/tickets${query ? `?${query}` : ''}`;

        return await this.request(endpoint);
    }

    /**
     * Получение тикета по ID
     */
    async getTicket(ticketId) {
        return await this.request(`/tickets/${ticketId}`);
    }

    /**
     * Создание нового тикета
     */
    async createTicket(ticketData) {
        return await this.request('/tickets', {
            method: 'POST',
            body: JSON.stringify(ticketData)
        });
    }

    /**
     * Обновление тикета
     */
    async updateTicket(ticketId, ticketData) {
        return await this.request(`/tickets/${ticketId}`, {
            method: 'PUT',
            body: JSON.stringify(ticketData)
        });
    }

    /**
     * Получение сообщений тикета
     */
    async getTicketMessages(ticketId, params = {}) {
        const searchParams = new URLSearchParams();
        
        Object.entries(params).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                searchParams.append(key, value);
            }
        });

        const query = searchParams.toString();
        const endpoint = `/tickets/${ticketId}/messages${query ? `?${query}` : ''}`;

        return await this.request(endpoint);
    }

    /**
     * Добавление сообщения в тикет
     */
    async addMessage(ticketId, messageData) {
        return await this.request(`/tickets/${ticketId}/messages`, {
            method: 'POST',
            body: JSON.stringify(messageData)
        });
    }

    /**
     * Получение категорий
     */
    async getCategories() {
        return await this.request('/categories');
    }

    /**
     * Проверка наличия токена авторизации
     */
    isAuthenticated() {
        return !!this.token;
    }

    /**
     * Выход из системы
     */
    logout() {
        this.token = null;
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
    }

    /**
     * Показ уведомления пользователю
     */
    showNotification(message, type = 'info') {
        const webApp = window.Telegram?.WebApp;
        
        if (webApp?.showAlert) {
            webApp.showAlert(message);
        } else {
            // Fallback для тестирования вне Telegram
            console.log(`[${type.toUpperCase()}] ${message}`);
            alert(message);
        }
    }

    /**
     * Показ popup с подтверждением
     */
    showConfirm(message) {
        return new Promise((resolve) => {
            const webApp = window.Telegram?.WebApp;
            
            if (webApp?.showConfirm) {
                webApp.showConfirm(message, resolve);
            } else {
                // Fallback для тестирования вне Telegram
                resolve(confirm(message));
            }
        });
    }

    /**
     * Обратная связь (haptic feedback)
     */
    hapticFeedback(type = 'light') {
        const webApp = window.Telegram?.WebApp;
        
        if (webApp?.HapticFeedback) {
            try {
                switch (type) {
                    case 'light':
                        webApp.HapticFeedback.impactOccurred('light');
                        break;
                    case 'medium':
                        webApp.HapticFeedback.impactOccurred('medium');
                        break;
                    case 'heavy':
                        webApp.HapticFeedback.impactOccurred('heavy');
                        break;
                    case 'success':
                        webApp.HapticFeedback.notificationOccurred('success');
                        break;
                    case 'error':
                        webApp.HapticFeedback.notificationOccurred('error');
                        break;
                    case 'warning':
                        webApp.HapticFeedback.notificationOccurred('warning');
                        break;
                }
            } catch (e) {
                console.warn('Haptic feedback не поддерживается:', e);
            }
        }
    }
}

// Создаем глобальный экземпляр API
window.api = new API();

// Экспортируем класс для использования в модулях
if (typeof module !== 'undefined' && module.exports) {
    module.exports = API;
}