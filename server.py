import os
import sys
import database
from app import app
from waitress import serve

def run_production_server(port=80, host='0.0.0.0'):
    database.init_db()
    print("=" * 60)
    print("  3D GALLERY HUB - PRODUCTION WSGI SERVER (Waitress)")
    print("=" * 60)
    print(f"Сервер запущено на: http://{host}:{port}")
    if port == 80:
        print("Стандартний веб-порт 80 активний!")
        print("Сайт доступний без вказування порту у браузері.")
    print("Для зупинки сервера натисніть Ctrl+C")
    print("=" * 60)
    
    try:
        serve(app, host=host, port=port, threads=8)
    except PermissionError:
        print(f"\n[УВАГА] Порт {port} потребує прав адміністратора.")
        print("Запуск на резервному порту 5000...")
        serve(app, host=host, port=5000, threads=8)

if __name__ == '__main__':
    port = 80
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    run_production_server(port=port)
