@echo off
chcp 65001 > nul
title 3D Model Catalog & Gallery Server

echo ========================================================
echo        3D MODEL GALLERY HUB - СЕРВЕР ЗАПУСКУ
echo ========================================================
echo.

python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ПОМИЛКА] Не вдалося встановити залежності.
    pause
    exit /b
)

echo.
echo Перевірка та ініціалізація бази даних SQLite...
python seed_data.py

echo.
echo [OK] Запуск веб-сервера 3D Галереї...
echo Відкрийте у браузері: http://127.0.0.1:5000
echo.
start http://127.0.0.1:5000
python app.py

pause
