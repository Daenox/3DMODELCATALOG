@echo off
chcp 65001 > nul
cd /d "%~dp0"
title 3D Gallery Hub Server (Port 80)

echo ========================================================
echo   3D GALLERY HUB - ЗАПУСК НА ПОРТУ 80 (ВЛАСНИЙ ДОМЕН)
echo ========================================================
echo.

python -m pip install -r requirements.txt >nul 2>&1
python seed_data.py >nul 2>&1

echo [OK] Відкриваємо браузер: http://3dgallery.local
start http://3dgallery.local
python server.py 80

pause
