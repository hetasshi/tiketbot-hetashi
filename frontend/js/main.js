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
            createTicketBtn: document.getElementById('createTicketBtn'),
            createFirstTicketBtn: document.getElementById('createFirstTicketBtn'),
            retryBtn: document.getElementById('retryBtn'),
            errorMessage: document.getElementById('errorMessage'),
            filterButtons: document.querySelectorAll('.filter__btn'),
            ticketTemplate: document.getElementById('ticketTemplate'),
            connectionStatus: document.getElementById('connectionStatus')
        };

        this.init();
    }

    /**
     * Инициализация приложения
     */
    async init() {
        try {
            // Настройка обработчиков событий
            this.setupEventListeners();

            // Инициализация WebSocket соединения
            this.setupWebSocket();

            // Попытка авторизации
            await this.authenticate();

            // Загрузка тикетов
            await this.loadTickets();

        } catch (error) {
            console.error('Ошибка инициализации:', error);
            this.showError('Ошибка загрузки приложения');
        }
    }

    /**
     * Настройка WebSocket соединения
     */
    setupWebSocket() {
        if (!window.wsClient) {
            console.warn('WebSocket клиент недоступен');
            return;
        }

        // Обновляем статус подключения
        this.updateConnectionStatus('connecting', 'Подключение...');

        // Обработчик успешного подключения
        window.wsClient.on('connection_established', (data) => {
            console.log('WebSocket подключен:', data);
            this.updateConnectionStatus('connected', 'Подключено');
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
            api.showNotification(`Новое сообщение в тикете "${data.ticket_title}"`);
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
        // Кнопки создания тикета
        this.elements.createTicketBtn?.addEventListener('click', () => {
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
            if (api.isAuthenticated()) {
                const user = await api.getCurrentUser();
                console.log('Пользователь авторизован:', user);
                return user;
            }

            // Авторизация через Telegram WebApp
            const authData = await api.authenticate();
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

            const params = {
                page: 1,
                size: this.pageSize
            };

            // Применяем фильтр если не "все"
            if (this.currentFilter !== 'all') {
                params.status = this.currentFilter;
            }

            const response = await api.getTickets(params);
            
            this.tickets = response.items || [];
            this.currentPage = 1;
            this.hasMoreTickets = response.page < response.pages;

            this.renderTickets();

        } catch (error) {
            console.error('Ошибка загрузки тикетов:', error);
            this.showError('Не удалось загрузить тикеты');
        } finally {
            this.isLoading = false;
        }
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

            const response = await api.getTickets(params);
            
            const newTickets = response.items || [];
            this.tickets = [...this.tickets, ...newTickets];
            this.currentPage++;
            this.hasMoreTickets = response.page < response.pages;

            this.renderTickets();

        } catch (error) {
            console.error('Ошибка загрузки дополнительных тикетов:', error);
            api.showNotification('Не удалось загрузить дополнительные тикеты', 'error');
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
        api.hapticFeedback('light');
    }

    /**
     * Отрисовка тикетов
     */
    renderTickets() {
        this.hideAllStates();

        if (this.tickets.length === 0) {
            this.showEmptyState();
            return;
        }

        this.showTicketsList();
        this.elements.ticketsContainer.innerHTML = '';

        this.tickets.forEach(ticket => {
            const ticketElement = this.createTicketElement(ticket);
            this.elements.ticketsContainer.appendChild(ticketElement);
        });

        // Показываем/скрываем кнопку "Загрузить еще"
        this.elements.loadMoreBtn.style.display = this.hasMoreTickets ? 'block' : 'none';
    }

    /**
     * Создание элемента тикета
     */
    createTicketElement(ticket) {
        const template = this.elements.ticketTemplate.content.cloneNode(true);
        const ticketElement = template.querySelector('.ticket');

        // Устанавливаем ID тикета
        ticketElement.dataset.ticketId = ticket.id;

        // Статус
        const statusElement = template.querySelector('.ticket__status');
        statusElement.dataset.status = ticket.status;
        statusElement.querySelector('.ticket__status-text').textContent = this.getStatusText(ticket.status);

        // Приоритет
        const priorityElement = template.querySelector('.ticket__priority');
        priorityElement.dataset.priority = ticket.priority;
        priorityElement.querySelector('.ticket__priority-text').textContent = this.getPriorityText(ticket.priority);

        // Заголовок и описание
        template.querySelector('.ticket__title').textContent = ticket.title;
        template.querySelector('.ticket__description').textContent = ticket.description;

        // Категория
        if (ticket.category) {
            template.querySelector('.ticket__category-icon').textContent = ticket.category.icon || '📋';
            template.querySelector('.ticket__category-name').textContent = ticket.category.name;
        }

        // Дата создания
        template.querySelector('.ticket__date').textContent = this.formatDate(ticket.created_at);

        // Количество сообщений
        const messagesCount = ticket.messages_count || 0;
        template.querySelector('.ticket__messages-text').textContent = `${messagesCount}`;

        return template;
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
        api.hapticFeedback('medium');
        
        // В полной версии здесь будет переход на страницу тикета
        // Пока что показываем уведомление
        api.showNotification(`Открытие тикета #${ticketId.slice(0, 8)}...`);
        
        // TODO: Реализовать переход на страницу деталей тикета
        // window.location.href = `ticket.html?id=${ticketId}`;
    }

    /**
     * Создание нового тикета
     */
    createTicket() {
        console.log('Создание нового тикета');
        
        // Haptic feedback
        api.hapticFeedback('medium');
        
        // В полной версии здесь будет переход на страницу создания
        api.showNotification('Функция создания тикета скоро будет доступна!');
        
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
document.addEventListener('DOMContentLoaded', () => {
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