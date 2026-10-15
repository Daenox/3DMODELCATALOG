@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion

title Налаштування власного локального домену (3dgallery.local)

echo ========================================================
echo   НАЛАШТУВАННЯ ВЛАСНОГО ДОМЕНУ: 3dgallery.local
echo ========================================================
echo.

:: Перевірка прав адміністратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ІНФО] Потрібні права адміністратора для додавання запису до hosts.
    echo Запитуємо підвищення прав...
    powershell -Command "Start-Process cmd -ArgumentList '/c \"\"%~f0\"\"' -Verb runAs"
    exit /b
)

set "HOSTS_FILE=%WINDIR%\System32\drivers\etc\hosts"
set "DOMAIN=3dgallery.local"
set "ENTRY=127.0.0.1 %DOMAIN%"

echo Перевірка файлу: %HOSTS_FILE%

findstr /C:"%DOMAIN%" "%HOSTS_FILE%" >nul 2>&1
if %errorLevel% equ 0 (
    echo.
    echo [OK] Домен %DOMAIN% вже налаштовано у вашій системі!
) else (
    echo.
    echo Додаємо запис "%ENTRY%" до %HOSTS_FILE%...
    echo. >> "%HOSTS_FILE%"
    echo # Локальний домен для сайту 3D галереї >> "%HOSTS_FILE%"
    echo %ENTRY% >> "%HOSTS_FILE%"
    echo [УСПІХ] Домен %DOMAIN% успішно додано!
)

echo.
echo ========================================================
echo Тепер ви можете відкривати сайт прямо за адресою:
echo 👉 http://%DOMAIN%
echo ========================================================
echo.
pause
