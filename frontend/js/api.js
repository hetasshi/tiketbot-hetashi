/**
 * API модуль для работы с backend Telegram Ticket Bot
 */

class API {
    constructor() {
        // Настройки API
        this.baseURL = null; // Будет загружен динамически
        this.token = null;
        this.configLoaded = false;
        
        // Инициализация при создании экземпляра
        this.init();
    }

    /**
     * Инициализация API
     */
    async init() {
        try {
            console.log('Инициализация API начата...');
            
            // Мобильная задержка для стабильности
            await new Promise(resolve => setTimeout(resolve, 500));
            
            // Загружаем конфигурацию с сервера
            await this.loadConfig();
            
            // Получаем токен из localStorage если есть
            this.token = localStorage.getItem('auth_token');
            
            // Telegram WebApp инициализация
            if (window.Telegram?.WebApp) {
                console.log('Инициализация Telegram WebApp...');
                
                // Готовность приложения
                window.Telegram.WebApp.ready();
                
                // Расширение до полного размера
                try {
                    window.Telegram.WebApp.expand();
                } catch (e) {
                    console.warn('Expand не поддерживается:', e);
                }
                
                // Применяем цветовую схему Telegram
                this.applyTelegramTheme();
                
                console.log('Telegram WebApp инициализирован');
            } else {
                console.log('Запуск вне Telegram WebApp (demo режим)');
            }
            
            console.log('API инициализирован успешно');
        } catch (error) {
            console.error('Ошибка инициализации API:', error);
            // Продолжаем работу с fallback настройками
            this.configLoaded = true;
        }
    }

    /**
     * Загрузка конфигурации с сервера
     */
    async loadConfig() {
        try {
            console.log('Загрузка конфигурации API...');
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 секунд таймаут
            
            const response = await fetch('/api/config', {
                headers: {
                    'ngrok-skip-browser-warning': 'true',
                    'Cache-Control': 'no-cache'
                },
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const config = await response.json();
            
            // Устанавливаем базовый URL для API
            this.baseURL = config.api_base + '/v1';
            this.configLoaded = true;
            
            console.log('Конфигурация API загружена:', config);
            console.log('API Base URL:', this.baseURL);
            
        } catch (error) {
            console.error('Ошибка загрузки конфигурации API:', error);
            
            // Fallback на ngrok URL если мы в Telegram
            if (window.Telegram?.WebApp) {
                this.baseURL = 'https://untabled-presuitably-owen.ngrok-free.app/api/v1';
                console.log('Fallback на ngrok URL:', this.baseURL);
            } else {
                // Fallback на localhost для разработки
                this.baseURL = 'http://127.0.0.1:8000/api/v1';
                console.log('Fallback на localhost:', this.baseURL);
            }
            
            this.configLoaded = true;
        }
    }

    /**
     * Ожидание загрузки конфигурации
     */
    async waitForConfig() {
        console.log('🔄 Ожидание загрузки конфигурации...');
        let attempts = 0;
        const maxAttempts = 100;
        
        while (!this.configLoaded && attempts < maxAttempts) {
            if (attempts % 10 === 0) {
                console.log(`🔄 Ожидание конфигурации, попытка ${attempts + 1}/${maxAttempts}`);
            }
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!this.configLoaded) {
            console.error('❌ Таймаут загрузки конфигурации');
            throw new Error('Configuration load timeout');
        }
        
        console.log('✅ Конфигурация загружена:', this.baseURL);
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
        try {
            webApp.setHeaderColor(webApp.themeParams.bg_color || '#ffffff');
        } catch (e) {
            console.warn('Header color не поддерживается:', e);
        }
        
        // Настраиваем главную кнопку (по умолчанию скрыта)
        webApp.MainButton.hide();
    }

    /**
     * Выполнение HTTP запроса
     */
    async request(endpoint, options = {}) {
        // Ожидаем загрузки конфигурации
        await this.waitForConfig();
        
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'ngrok-skip-browser-warning': 'true', // Обход ngrok предупреждения
                'Cache-Control': 'no-cache', // Принудительное обновление для мобильных
                ...options.headers
            },
            ...options
        };

        // Добавляем токен авторизации если есть
        if (this.token) {
            config.headers['Authorization'] = `Bearer ${this.token}`;
        }

        try {
            console.log('API request:', { url, method: config.method, headers: config.headers });
            
            const response = await fetch(url, config);
            
            console.log('API response status:', response.status);
            
            // Проверяем статус ответа
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch {
                    errorData = { message: `HTTP ${response.status} ${response.statusText}` };
                }
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }

            const data = await response.json();
            console.log('API response data:', data);
            return data;
            
        } catch (error) {
            console.error('API request failed:', {
                url,
                method: config.method,
                error: error.message,
                stack: error.stack
            });
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
        
        console.log('API getTickets - вызов:', {
            baseURL: this.baseURL,
            endpoint: endpoint,
            fullURL: `${this.baseURL}${endpoint}`,
            params: params
        });

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