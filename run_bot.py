#!/usr/bin/env python3
"""
TiketHet Telegram Bot Launcher
Универсальный запуск бота из корня проекта без настройки PYTHONPATH
"""

import os
import sys
from pathlib import Path

def main():
    print("[BOT] Starting TiketHet Telegram Bot...")
    
    # Получаем путь к корню проекта
    project_root = Path(__file__).parent.absolute()
    src_path = project_root / "src"
    
    # Добавляем src в Python path
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    print(f"[INFO] Project root: {project_root}")
    print(f"[INFO] Added to Python path: {src_path}")
    print()
    
    try:
        # Импортируем и запускаем бот
        from tikethet.telegram.bot import main as bot_main
        import asyncio
        
        # Запускаем бот
        asyncio.run(bot_main())
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("[INFO] Please check that all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n[INFO] Bot stopped by user")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()