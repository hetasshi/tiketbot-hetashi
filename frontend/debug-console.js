// Диагностический скрипт для консоли браузера

console.log('🔍 Начинаем диагностику TiketHet...');

// Проверяем окружение
console.log('📱 Telegram WebApp:', window.Telegram?.WebApp ? '✅ Доступен' : '❌ Недоступен');
console.log('🌐 User Agent:', navigator.userAgent);
console.log('📍 URL:', window.location.href);

// Проверяем API
console.log('\n🔧 Проверка API...');
if (window.api) {
    console.log('📦 API объект:', window.api);
    console.log('⚙️ configLoaded:', window.api.configLoaded);
    console.log('🔗 baseURL:', window.api.baseURL);
    console.log('🎫 token:', window.api.token ? '✅ Есть' : '❌ Нет');
} else {
    console.log('❌ API объект не найден');
}

// Проверяем WebSocket
console.log('\n🔌 Проверка WebSocket...');
if (window.wsClient) {
    console.log('📡 WebSocket клиент:', window.wsClient);
    console.log('🔗 isConnected:', window.wsClient.isConnected);
    console.log('🌐 baseUrl:', window.wsClient.baseUrl);
} else {
    console.log('❌ WebSocket клиент не найден');
}

// Проверяем TicketApp
console.log('\n🎫 Проверка TicketApp...');
if (window.ticketApp) {
    console.log('📋 TicketApp объект:', window.ticketApp);
    console.log('📊 tickets count:', window.ticketApp.tickets?.length || 0);
    console.log('🏃 isLoading:', window.ticketApp.isLoading);
} else {
    console.log('❌ TicketApp не найден');
}

// Тестируем сетевые запросы
console.log('\n🌐 Тестируем сетевые запросы...');

async function testNetwork() {
    try {
        console.log('📡 Тестируем /api/config...');
        const configResponse = await fetch('/api/config', {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        const config = await configResponse.json();
        console.log('✅ Конфигурация:', config);
        
        console.log('🎫 Тестируем /api/v1/tickets...');
        const ticketsResponse = await fetch(config.api_base + '/v1/tickets', {
            headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        const tickets = await ticketsResponse.json();
        console.log('✅ Тикеты:', tickets.items?.length || 0, 'шт.');
        
    } catch (error) {
        console.error('❌ Ошибка сети:', error);
    }
}

testNetwork();

console.log('\n🏁 Диагностика завершена. Проверьте результаты выше.');