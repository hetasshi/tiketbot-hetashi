@echo off
echo Starting TiketHet Telegram Bot...
echo.

cd /d "C:\Users\user\Desktop\tiketbot"
set PYTHONPATH=src
python -m tikethet.telegram.bot

echo.
echo Bot stopped. Press any key to exit.
pause >nul