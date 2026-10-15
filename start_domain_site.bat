@echo off
chcp 65001 > nul
title 3D Gallery Hub - Власний Домен

echo ========================================================
echo       ЗАПУСК 3D GALLERY ХАБУ НА ВЛАСНОМУ ДОМЕНІ
echo ========================================================
echo.

:: Перевірка прав адміністратора для порту 80
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [УВАГА] Для роботи на стандартному порту 80 (без вказування :5000 у браузері)
    echo рекомендовано запускати скрипт від імені адміністратора.
    echo Запускаємо з правами адміністратора...
    powershell -Command "Start-Process cmd -ArgumentList '/k \"\"%~dp0run_server_admin.bat\"\"' -Verb runAs"
    exit /b
)

:run_server
echo Встановлення/перевірка бібліотек...
python -m pip install -r requirements.txt >nul 2>&1

echo Ініціалізація бази даних...
python seed_data.py >nul 2>&1

echo.
echo [УСПІХ] Сервер запущено на власному домені!
echo Відкрийте сайт: http://3dgallery.local
echo.
start http://3dgallery.local
python server.py 80

pause
