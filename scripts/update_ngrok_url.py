#!/usr/bin/env python3
"""
Скрипт для автоматического обновления ngrok URL в конфигурации TiketHet.

Использование:
python scripts/update_ngrok_url.py https://abc123.ngrok.io
"""

import os
import sys
import re
from pathlib import Path

def update_env_file(new_url: str) -> bool:
    """
    Обновляет FRONTEND_URL в .env файле.
    
    Args:
        new_url: Новый ngrok URL
        
    Returns:
        bool: True если обновление успешно
    """
    env_path = Path('deployment/config/.env')
    
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return False
    
    # Читаем содержимое
    with open(env_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем FRONTEND_URL
    old_pattern = r'FRONTEND_URL=.*'
    new_line = f'FRONTEND_URL={new_url}'
    
    if re.search(old_pattern, content):
        # Заменяем существующую строку
        new_content = re.sub(old_pattern, new_line, content)
        print(f"[OK] Обновлен FRONTEND_URL в .env")
    else:
        # Добавляем новую строку
        new_content = content + f'\n{new_line}\n'
        print(f"[OK] Добавлен FRONTEND_URL в .env")
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


def update_websocket_js(new_url: str) -> bool:
    """
    WebSocket URL теперь загружается автоматически из /api/config.
    Этот метод оставлен для обратной совместимости.
    
    Args:
        new_url: Новый ngrok URL (игнорируется)
        
    Returns:
        bool: True всегда
    """
    print("[OK] WebSocket URL теперь загружается автоматически из API конфигурации")
    print("   Нет необходимости вручную обновлять frontend/js/websocket.js")
    return True


def validate_url(url: str) -> bool:
    """
    Проверяет корректность URL.
    
    Args:
        url: URL для проверки
        
    Returns:
        bool: True если URL корректный
    """
    if not url.startswith(('http://', 'https://')):
        print("❌ URL должен начинаться с http:// или https://")
        return False
    
    if 'ngrok.io' not in url and 'localhost' not in url:
        print("⚠️ Предупреждение: URL не содержит ngrok.io или localhost")
    
    return True


def main():
    """Основная функция скрипта."""
    if len(sys.argv) != 2:
        print("Скрипт обновления ngrok URL для TiketHet")
        print("")
        print("Использование:")
        print("  python scripts/update_ngrok_url.py https://abc123.ngrok.io")
        print("")
        print("Что делает скрипт:")
        print("  • Обновляет FRONTEND_URL в .env файле")
        print("  • Обновляет WebSocket URL в frontend/js/websocket.js")
        print("  • Проверяет корректность URL")
        print("")
        print("После выполнения скрипта перезапустите:")
        print("  • WebSocket сервер: python src/servers/websocket_server.py") 
        print("  • Telegram бот: python -m src.tikethet.telegram.bot")
        sys.exit(1)
    
    new_url = sys.argv[1].rstrip('/')  # Убираем слеш в конце
    
    print(f"Обновление конфигурации на URL: {new_url}")
    print("")
    
    # Проверяем URL
    if not validate_url(new_url):
        sys.exit(1)
    
    # Проверяем рабочую директорию
    if not Path('deployment/config/.env').exists():
        print("❌ Запустите скрипт из корневой папки проекта (где находится deployment/config/.env)")
        sys.exit(1)
    
    success = True
    
    # Обновляем .env файл
    if not update_env_file(new_url):
        success = False
    
    # Обновляем WebSocket JavaScript
    if not update_websocket_js(new_url):
        success = False
    
    if success:
        print("")
        print("Конфигурация успешно обновлена!")
        print("")
        print("Следующие шаги:")
        print("1. Перезапустите WebSocket сервер:")
        print("   python src/servers/websocket_server.py")
        print("")
        print("2. В новом терминале перезапустите бота:")
        print("   python -m src.tikethet.telegram.bot") 
        print("")
        print("3. Проверьте работу Mini App в Telegram")
        print("   /tickets -> кнопка 'Открыть тикеты'")
    else:
        print("")
        print("Обновление завершено с ошибками!")
        sys.exit(1)


if __name__ == "__main__":
    main()