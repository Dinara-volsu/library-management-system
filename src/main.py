"""
Главный файл для запуска приложения
"""
import sys
import argparse
from src.ui.console.main_menu import ConsoleUI
from src.ui.web.app import app as web_app


def main():
    """Главная функция запуска приложения"""
    parser = argparse.ArgumentParser(description='Система управления библиотечным каталогом')
    parser.add_argument('--mode', choices=['console', 'web'], default='console',
                       help='Режим запуска: console (консоль) или web (веб-интерфейс)')
    parser.add_argument('--port', type=int, default=5000,
                       help='Порт для веб-сервера (только для режима web)')
    
    args = parser.parse_args()
    
    if args.mode == 'console':
        # Запуск консольного интерфейса
        console_ui = ConsoleUI()
        console_ui.show_main_menu()
    elif args.mode == 'web':
        # Запуск веб-интерфейса
        print(f"🚀 Запуск веб-сервера на http://localhost:{args.port}")
        print("📖 Откройте браузер и перейдите по указанному адресу")
        web_app.run(debug=True, port=args.port)
    else:
        print("❌ Неизвестный режим запуска")
        sys.exit(1)


if __name__ == '__main__':
    main()
