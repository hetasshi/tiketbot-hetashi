/**
 * Основной скрипт Telegram Ticket Bot Mini App
 */

class TicketApp {
    constructor() {
        this.tickets = [];
        this.currentFilter = 'all';
        this.isLoading = false;
        this.currentPage = 1;
        this.pageSize = 20;
        this.hasMoreTickets = false;

        // DOM элементы
        this.elements = {
            loading: document.getElementById('loading'),
            error: document.getElementById('error'),
            emptyState: document.getElementById('emptyState'),
            ticketsList: document.getElementById('ticketsList'),
            ticketsContainer: document.getElementById('ticketsContainer'),
            loadMoreBtn: document.getElementById('loadMoreBtn'),
            fabCreateTicket: document.getElementById('fabCreateTicket'),
            createFirstTicketBtn: document.getElementById('createFirstTicketBtn'),
            retryBtn: document.getElementById('retryBtn'),
            errorMessage: document.getElementById('errorMessage'),
            filterButtons: document.querySelectorAll('.filter__btn'),
            ticketTemplate: document.getElementById('ticketTemplate'),
            connectionStatus: document.getElementById('connectionStatus')
        };
        
        // Проверяем, что все ключевые элементы найдены
        const missingElements = [];
        if (!this.elements.loading) missingElements.push('loading');
        if (!this.elements.error) missingElements.push('error');
        if (!this.elements.emptyState) missingElements.push('emptyState');
        if (!this.elements.ticketsList) missingElements.push('ticketsList');
        if (!this.elements.ticketsContainer) missingElements.push('ticketsContainer');
        if (!this.elements.ticketTemplate) missingElements.push('ticketTemplate');
        
        if (missingElements.length > 0) {
            console.error('Не найдены DOM элементы:', missingElements);
        } else {
            console.log('Все ключевые DOM элементы найдены');
        }

        this.init();
    }

    /**
     * Инициализация приложения
     */
    async init() {
        try {
            console.log('Инициализация TicketApp начата...');
            
            // Добавляем небольшую задержку для стабильности на мобильных
            await new Promise(resolve => setTimeout(resolve, 100));
            
            // Ожидаем инициализации API с таймаутом
            if (window.api && !window.api.configLoaded) {
                console.log('Ожидаем загрузки конфигурации API...');
                const timeout = new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('API timeout')), 10000)
                );
                
                try {
                    await Promise.race([
                        window.api.waitForConfig(),
                        timeout
                    ]);
                    console.log('Конфигурация API загружена');
                } catch (timeoutError) {
                    console.warn('Таймаут загрузки API, продолжаем с fallback');
                }
            }
            
            // Настройка обработчиков событий
            this.setupEventListeners();

            // Инициализация WebSocket соединения (с задержкой)
            setTimeout(() => this.setupWebSocket(), 1000);

            // Попытка авторизации
            await this.authenticate();

            // Загрузка тикетов
            await this.loadTickets();

            console.log('Инициализация TicketApp завершена успешно');

        } catch (error) {
            console.error('Ошибка инициализации:', error);
            this.showError(`Ошибка загрузки приложения: ${error.message}`);
        }
    }

    /**
     * Настройка WebSocket соединения
     */
    setupWebSocket() {
        if (!window.wsClient) {
            console.warn('WebSocket клиент недоступен');
            this.updateConnectionStatus('disconnected', 'WebSocket недоступен');
            return;
        }

        console.log('Настройка WebSocket соединения...');
        
        // Обновляем статус подключения
        this.updateConnectionStatus('connecting', 'Подключение...');

        // Обработчик успешного подключения
        window.wsClient.on('connection_established', (data) => {
            console.log('WebSocket подключен:', data);
            this.updateConnectionStatus('connected', 'Подключено');
            
            // Haptic feedback для подтверждения подключения
            if (window.api) {
                window.api.hapticFeedback('light');
            }
        });

        // Обработчик отключения
        window.wsClient.on('disconnect', (data) => {
            console.log('WebSocket отключен:', data);
            this.updateConnectionStatus('disconnected', 'Не подключено');
        });

        // Обработчик ошибок
        window.wsClient.on('error', (data) => {
            console.error('Ошибка WebSocket:', data);
            this.updateConnectionStatus('disconnected', 'Ошибка соединения');
        });

        // Обработчик обновлений тикетов
        window.wsClient.on('ticket_status_changed', (data) => {
            this.handleTicketUpdate(data);
        });

        // Обработчик новых сообщений
        window.wsClient.on('new_ticket_message', (data) => {
            console.log('Новое сообщение в тикете:', data);
            // Показываем уведомление
            if (window.api) {
                window.api.showNotification(`Новое сообщение в тикете "${data.ticket_title}"`);
            }
        });
    }

    /**
     * Обновление статуса подключения
     */
    updateConnectionStatus(status, text) {
        if (!this.elements.connectionStatus) return;

        // Обновляем класс статуса
        this.elements.connectionStatus.className = `connection-status connection-status--${status}`;
        
        // Обновляем текст
        const statusText = this.elements.connectionStatus.querySelector('.connection-status__text');
        if (statusText) {
            statusText.textContent = text;
        }
    }

    /**
     * Настройка обработчиков событий
     */
    setupEventListeners() {
        // FAB кнопка создания тикета
        this.elements.fabCreateTicket?.addEventListener('click', () => {
            this.createTicket();
        });
        
        this.elements.createFirstTicketBtn?.addEventListener('click', () => {
            this.createTicket();
        });

        // Кнопка повтора загрузки
        this.elements.retryBtn?.addEventListener('click', () => {
            this.loadTickets();
        });

        // Кнопка загрузки дополнительных тикетов
        this.elements.loadMoreBtn?.addEventListener('click', () => {
            this.loadMoreTickets();
        });

        // Фильтры
        this.elements.filterButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const status = e.target.dataset.status;
                this.setFilter(status);
            });
        });

        // Обработка кликов по тикетам (делегирование событий)
        this.elements.ticketsContainer?.addEventListener('click', (e) => {
            const ticketElement = e.target.closest('.ticket');
            if (ticketElement) {
                const ticketId = ticketElement.dataset.ticketId;
                this.openTicket(ticketId);
            }
        });
    }

    /**
     * Авторизация пользователя
     */
    async authenticate() {
        try {
            // Если токен уже есть, проверим его
            if (window.api.isAuthenticated()) {
                const user = await window.api.getCurrentUser();
                console.log('Пользователь авторизован:', user);
                return user;
            }

            // Авторизация через Telegram WebApp
            const authData = await window.api.authenticate();
            console.log('Авторизация успешна:', authData.user);
            
            return authData.user;
            
        } catch (error) {
            console.error('Ошибка авторизации:', error);
            
            // Для тестирования вне Telegram показываем demo режим
            if (!window.Telegram?.WebApp) {
                console.warn('Запуск в demo режиме (вне Telegram)');
                return this.mockUser();
            }
            
            throw error;
        }
    }

    /**
     * Mock пользователь для тестирования
     */
    mockUser() {
        return {
            id: 'demo-user',
            telegram_id: 123456789,
            first_name: 'Demo',
            last_name: 'User',
            role: 'USER'
        };
    }

    /**
     * Загрузка тикетов
     */
    async loadTickets() {
        if (this.isLoading) return;

        try {
            this.isLoading = true;
            this.showLoading();
            
            // Проверяем, что API доступен
            if (!window.api) {
                throw new Error('API не доступен');
            }
            
            // Ожидаем готовности API
            if (!window.api.configLoaded) {
                console.log('Ожидаем загрузки конфигурации API...');
                await this.waitForAPIConfig();
                console.log('Конфигурация API готова, baseURL:', window.api.baseURL);
            }
            
            // Проверяем, что baseURL установлен
            if (!window.api.baseURL) {
                throw new Error('API baseURL не установлен');
            }

            const params = {
                page: 1,
                size: this.pageSize
            };

            // Применяем фильтр если не "все"
            if (this.currentFilter !== 'all') {
                params.status = this.currentFilter;
            }
            
            console.log('Запрос тикетов с параметрами:', params);
            console.log('API baseURL:', window.api.baseURL);
            
            const response = await window.api.getTickets(params);
            console.log('Ответ от API:', response);
            
            this.tickets = response.items || [];
            this.currentPage = 1;
            this.hasMoreTickets = response.page < response.pages;

            this.renderTickets();

        } catch (error) {
            console.error('\ud83d\udd34 Ошибка загрузки тикетов:', error);
            this.showError(`Не удалось загрузить тикеты: ${error.message}`);
        } finally {
            this.isLoading = false;
        }
    }

    /**
     * Ожидание готовности API конфигурации
     */
    async waitForAPIConfig() {
        const maxAttempts = 100;
        let attempts = 0;
        
        while (!window.api.configLoaded && attempts < maxAttempts) {
            console.log(`Ожидание конфигурации API, попытка ${attempts + 1}...`);
            await new Promise(resolve => setTimeout(resolve, 100));
            attempts++;
        }
        
        if (!window.api.configLoaded) {
            console.error('❌ Таймаут загрузки API конфигурации');
            throw new Error('API configuration timeout');
        }
        
        console.log('✅ API конфигурация загружена');
    }

    /**
     * Загрузка дополнительных тикетов
     */
    async loadMoreTickets() {
        if (this.isLoading || !this.hasMoreTickets) return;

        try {
            this.isLoading = true;
            this.elements.loadMoreBtn.textContent = 'Загружаем...';

            const params = {
                page: this.currentPage + 1,
                size: this.pageSize
            };

            if (this.currentFilter !== 'all') {
                params.status = this.currentFilter;
            }

            const response = await window.api.getTickets(params);
            
            const newTickets = response.items || [];
            this.tickets = [...this.tickets, ...newTickets];
            this.currentPage++;
            this.hasMoreTickets = response.page < response.pages;

            this.renderTickets();

        } catch (error) {
            console.error('Ошибка загрузки дополнительных тикетов:', error);
            window.api.showNotification('Не удалось загрузить дополнительные тикеты', 'error');
        } finally {
            this.isLoading = false;
            this.elements.loadMoreBtn.textContent = 'Загрузить еще';
        }
    }

    /**
     * Установка фильтра
     */
    async setFilter(status) {
        if (this.currentFilter === status) return;

        // Обновляем активный фильтр
        this.elements.filterButtons.forEach(btn => {
            btn.classList.toggle('filter__btn--active', btn.dataset.status === status);
        });

        this.currentFilter = status;
        await this.loadTickets();
        
        // Haptic feedback
        window.api.hapticFeedback('light');
    }

    /**
     * Отрисовка тикетов
     */
    renderTickets() {
        try {
            console.log('Отрисовка тикетов, количество:', this.tickets.length);
            
            this.hideAllStates();

            if (this.tickets.length === 0) {
                console.log('Нет тикетов, показываем empty state');
                this.showEmptyState();
                return;
            }

            console.log('Показываем список тикетов');
            this.showTicketsList();
            
            if (!this.elements.ticketsContainer) {
                console.error('Не найден элемент ticketsContainer');
                return;
            }
            
            this.elements.ticketsContainer.innerHTML = '';

            this.tickets.forEach((ticket, index) => {
                try {
                    console.log(`Отрисовка тикета ${index + 1}:`, ticket);
                    const ticketElement = this.createTicketElement(ticket);
                    this.elements.ticketsContainer.appendChild(ticketElement);
                } catch (error) {
                    console.error(`Ошибка отрисовки тикета ${ticket.id}:`, error);
                }
            });

            // Показываем/скрываем кнопку "Загрузить еще"
            if (this.elements.loadMoreBtn) {
                this.elements.loadMoreBtn.style.display = this.hasMoreTickets ? 'block' : 'none';
            }
            
            console.log('Отрисовка завершена');
        } catch (error) {
            console.error('Ошибка в renderTickets:', error);
        }
    }

    /**
     * Создание элемента тикета
     */
    createTicketElement(ticket) {
        try {
            console.log('Создание элемента тикета:', ticket);
            
            if (!this.elements.ticketTemplate) {
                throw new Error('Не найден шаблон ticketTemplate');
            }
            
            const template = this.elements.ticketTemplate.content.cloneNode(true);
            const ticketElement = template.querySelector('.ticket');
            
            if (!ticketElement) {
                throw new Error('Не найден .ticket в шаблоне');
            }

            // Устанавливаем ID тикета
            ticketElement.dataset.ticketId = ticket.id;

            // Статус
            const statusElement = template.querySelector('.ticket__status');
            const statusText = template.querySelector('.ticket__status-text');
            if (statusElement && statusText) {
                statusElement.dataset.status = ticket.status;
                statusText.textContent = this.getStatusText(ticket.status);
            }

            // Приоритет
            const priorityElement = template.querySelector('.ticket__priority');
            const priorityText = template.querySelector('.ticket__priority-text');
            if (priorityElement && priorityText) {
                priorityElement.dataset.priority = ticket.priority;
                priorityText.textContent = this.getPriorityText(ticket.priority);
            }

            // Заголовок и описание
            const titleElement = template.querySelector('.ticket__title');
            const descriptionElement = template.querySelector('.ticket__description');
            if (titleElement) titleElement.textContent = ticket.title;
            if (descriptionElement) descriptionElement.textContent = ticket.description;

            // Категория
            if (ticket.category) {
                const categoryIcon = template.querySelector('.ticket__category-icon');
                const categoryName = template.querySelector('.ticket__category-name');
                if (categoryIcon) categoryIcon.textContent = ticket.category.icon || '📋';
                if (categoryName) categoryName.textContent = ticket.category.name;
            }

            // Дата создания
            const dateElement = template.querySelector('.ticket__date');
            if (dateElement) dateElement.textContent = this.formatDate(ticket.created_at);

            // Количество сообщений
            const messagesCount = ticket.messages_count || 0;
            const messagesText = template.querySelector('.ticket__messages-text');
            if (messagesText) messagesText.textContent = `${messagesCount}`;

            console.log('Элемент тикета создан успешно');
            return template;
        } catch (error) {
            console.error('Ошибка создания элемента тикета:', error);
            throw error;
        }
    }

    /**
     * Получение текста статуса
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
     * Получение текста приоритета
     */
    getPriorityText(priority) {
        const priorityMap = {
            'LOW': 'Низкий',
            'NORMAL': 'Обычный',
            'HIGH': 'Высокий',
            'CRITICAL': 'Критический'
        };
        return priorityMap[priority] || priority;
    }

    /**
     * Форматирование даты
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);

        if (diffInHours < 1) {
            return 'только что';
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)} ч. назад`;
        } else if (diffInHours < 48) {
            return 'вчера';
        } else {
            return date.toLocaleDateString('ru-RU', {
                day: '2-digit',
                month: '2-digit',
                year: '2-digit'
            });
        }
    }

    /**
     * Открытие тикета
     */
    openTicket(ticketId) {
        console.log('Открываем тикет:', ticketId);
        
        // Haptic feedback
        window.api.hapticFeedback('medium');
        
        // В полной версии здесь будет переход на страницу тикета
        // Пока что показываем уведомление
        window.api.showNotification(`Открытие тикета #${ticketId.slice(0, 8)}...`);
        
        // TODO: Реализовать переход на страницу деталей тикета
        // window.location.href = `ticket.html?id=${ticketId}`;
    }

    /**
     * Создание нового тикета
     */
    createTicket() {
        console.log('Создание нового тикета');
        
        // Haptic feedback
        window.api.hapticFeedback('medium');
        
        // В полной версии здесь будет переход на страницу создания
        window.api.showNotification('Функция создания тикета скоро будет доступна!');
        
        // TODO: Реализовать переход на страницу создания тикета
        // window.location.href = 'create-ticket.html';
    }

    /**
     * Обработка обновлений тикетов через WebSocket
     */
    handleTicketUpdate(data) {
        console.log('Обработка обновления тикета:', data);
        
        const ticketId = data.ticket_id;
        
        // Находим тикет в текущем списке
        const ticketIndex = this.tickets.findIndex(ticket => ticket.id === ticketId);
        
        if (ticketIndex !== -1) {
            // Обновляем статус тикета
            this.tickets[ticketIndex].status = data.new_status;
            this.tickets[ticketIndex].updated_at = data.timestamp;
            
            // Перерисовываем интерфейс если тикеты отображены
            if (this.elements.ticketsList.style.display !== 'none') {
                this.renderTickets();
            }
            
            // Показываем уведомление если изменение не от текущего пользователя
            if (data.updated_by !== 'demo-user') {
                this.showTicketUpdateNotification(data);
            }
        }
    }

    /**
     * Показ уведомления об обновлении тикета
     */
    showTicketUpdateNotification(data) {
        // Создаем всплывающее уведомление
        const notification = document.createElement('div');
        notification.className = 'ticket-update-notification';
        notification.innerHTML = `
            <div class="ticket-update-notification__content">
                <div class="ticket-update-notification__title">Тикет обновлен</div>
                <div class="ticket-update-notification__message">
                    "${data.ticket_title}" - статус изменен на "${this.getStatusText(data.new_status)}"
                </div>
            </div>
        `;
        
        // Добавляем стили для уведомления
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--tg-button);
            color: var(--tg-button-text);
            padding: var(--space-md);
            border-radius: var(--radius-md);
            box-shadow: var(--shadow-lg);
            z-index: 1000;
            animation: slideIn 0.3s ease;
            max-width: 300px;
        `;
        
        document.body.appendChild(notification);
        
        // Убираем уведомление через 4 секунды
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }

    /**
     * Показать состояние загрузки
     */
    showLoading() {
        this.hideAllStates();
        this.elements.loading.style.display = 'block';
    }

    /**
     * Показать ошибку
     */
    showError(message) {
        this.hideAllStates();
        this.elements.errorMessage.textContent = message;
        this.elements.error.style.display = 'block';
    }

    /**
     * Показать пустое состояние
     */
    showEmptyState() {
        this.hideAllStates();
        this.elements.emptyState.style.display = 'block';
    }

    /**
     * Показать список тикетов
     */
    showTicketsList() {
        this.hideAllStates();
        this.elements.ticketsList.style.display = 'block';
    }

    /**
     * Скрыть все состояния
     */
    hideAllStates() {
        this.elements.loading.style.display = 'none';
        this.elements.error.style.display = 'none';
        this.elements.emptyState.style.display = 'none';
        this.elements.ticketsList.style.display = 'none';
    }
}

// Инициализация приложения после загрузки DOM
document.addEventListener('DOMContentLoaded', async () => {
    console.log('DOM загружен, инициализируем приложение...');
    
    // Ожидаем полной инициализации API с увеличенным таймаутом
    let attempts = 0;
    const maxAttempts = 100; // 10 секунд максимум
    
    while ((!window.api || !window.api.configLoaded) && attempts < maxAttempts) {
        console.log(`Ожидание инициализации API, попытка ${attempts + 1}...`);
        await new Promise(resolve => setTimeout(resolve, 100));
        attempts++;
        
        // Если API существует, но конфигурация не загружена, попробуем дождаться
        if (window.api && typeof window.api.waitForConfig === 'function' && !window.api.configLoaded) {
            try {
                console.log('Вызываем waitForConfig...');
                await window.api.waitForConfig();
                break;
            } catch (error) {
                console.error('Ошибка в waitForConfig:', error);
                // Продолжаем цикл ожидания
            }
        }
    }
    
    if (!window.api) {
        console.error('❌ API не инициализирован после ожидания');
        return;
    }
    
    if (!window.api.configLoaded) {
        console.warn('⚠️ API конфигурация не загружена, но продолжаем...');
    }
    
    console.log('✅ API готов, создаем TicketApp...');
    console.log('API baseURL:', window.api.baseURL);
    window.ticketApp = new TicketApp();
});

// Обработка ошибок на уровне приложения
window.addEventListener('error', (event) => {
    console.error('Глобальная ошибка:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Неотработанная ошибка Promise:', event.reason);
});

// Экспорт для тестирования
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TicketApp;
}