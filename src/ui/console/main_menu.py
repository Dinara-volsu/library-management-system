"""
Консольный интерфейс для системы каталога
"""
import sys
import os
from datetime import datetime
from ...api.library_api import LibraryAPI


class ConsoleUI:
    """Класс консольного интерфейса"""
    
    def __init__(self):
        self.api = LibraryAPI()
        self.is_running = True
    
    def clear_screen(self):
        """Очистить экран консоли"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str):
        """Вывести заголовок"""
        print("\n" + "=" * 50)
        print(f"{title:^50}")
        print("=" * 50 + "\n")
    
    def show_main_menu(self):
        """Главное меню"""
        while self.is_running:
            self.clear_screen()
            
            if self.api.get_current_user():
                current_user = self.api.get_current_user()
                print(f"👤 Текущий пользователь: {current_user.full_name}")
                print(f"   Роль: {'Администратор' if current_user.is_admin() else 'Читатель'}\n")
            
            self.print_header("📚 СИСТЕМА УПРАВЛЕНИЯ БИБЛИОТЕКОЙ")
            
            print("1. 🔍 Поиск книг")
            print("2. 📅 Мои бронирования")
            
            if not self.api.get_current_user():
                print("3. 🔐 Войти в систему")
                print("4. 📝 Зарегистрироваться")
            else:
                if self.api.get_current_user().is_admin():
                    print("3. 📚 Добавить новую книгу")
                    print("4. 🗑️ Списать книгу")
                    print("5. ✅ Подтвердить бронирование")
                    print("6. 🚪 Выйти из системы")
                else:
                    print("3. 📖 Забронировать книгу")
                    print("4. 🚪 Выйти из системы")
            
            print("0. ❌ Выход из программы")
            
            choice = input("\nВыберите действие: ")
            
            if choice == "1":
                self.search_books_menu()
            elif choice == "2":
                self.show_my_reservations()
            elif choice == "3":
                if not self.api.get_current_user():
                    self.login_menu()
                elif self.api.get_current_user().is_admin():
                    self.add_book_menu()
                else:
                    self.reserve_book_menu()
            elif choice == "4":
                if not self.api.get_current_user():
                    self.register_menu()
                elif self.api.get_current_user().is_admin():
                    self.write_off_book_menu()
                else:
                    self.logout()
            elif choice == "5" and self.api.get_current_user() and self.api.get_current_user().is_admin():
                self.confirm_reservation_menu()
            elif choice == "6" and self.api.get_current_user() and self.api.get_current_user().is_admin():
                self.logout()
            elif choice == "0":
                self.exit_program()
            else:
                print("\n❌ Неверный выбор. Попробуйте снова.")
                input("Нажмите Enter для продолжения...")
    
    def search_books_menu(self):
        """Меню поиска книг"""
        self.clear_screen()
        self.print_header("🔍 ПОИСК КНИГ")
        
        print("Критерии поиска (оставьте пустым для пропуска):")
        
        title = input("Название: ").strip()
        author = input("Автор: ").strip()
        year_input = input("Год издания: ").strip()
        genre = input("Жанр: ").strip()
        
        year = int(year_input) if year_input.isdigit() else None
        
        # Выполняем поиск
        books = self.api.search_books(
            query=title or author,
            year=year,
            genre=genre if genre else None
        )
        
        if not books:
            print("\n📭 Книги не найдены")
        else:
            print(f"\n📚 Найдено книг: {len(books)}")
            print("-" * 80)
            
            for i, book in enumerate(books, 1):
                status = "✅ Доступна" if book.available > 0 else "⛔ Нет в наличии"
                print(f"{i}. {book.title}")
                print(f"   Автор: {book.author} | Год: {book.year} | Жанр: {book.genre}")
                print(f"   Издательство: {book.publisher} | Страниц: {book.pages}")
                print(f"   ISBN: {book.isbn} | Статус: {status}")
                print(f"   В наличии: {book.available}/{book.quantity}")
                print("-" * 80)
        
        input("\nНажмите Enter для возврата в меню...")
    
    def login_menu(self):
        """Меню входа в систему"""
        self.clear_screen()
        self.print_header("🔐 ВХОД В СИСТЕМУ")
        
        username = input("Имя пользователя: ").strip()
        password = input("Пароль: ").strip()
        
        user = self.api.login(username, password)
        
        if user:
            print(f"\n✅ Успешный вход! Добро пожаловать, {user.full_name}!")
        else:
            print("\n❌ Неверное имя пользователя или пароль")
        
        input("\nНажмите Enter для продолжения...")
    
    def register_menu(self):
        """Меню регистрации"""
        self.clear_screen()
        self.print_header("📝 РЕГИСТРАЦИЯ")
        
        print("Заполните данные для регистрации:")
        
        username = input("Имя пользователя: ").strip()
        email = input("Email: ").strip()
        password = input("Пароль: ").strip()
        full_name = input("Полное имя: ").strip()
        phone = input("Телефон (необязательно): ").strip() or None
        
        if not all([username, email, password, full_name]):
            print("\n❌ Все обязательные поля должны быть заполнены!")
        else:
            user = self.api.register(username, email, password, full_name, phone)
            
            if user:
                print(f"\n✅ Регистрация успешна! Добро пожаловать, {user.full_name}!")
                print("Теперь вы можете войти в систему.")
            else:
                print("\n❌ Ошибка регистрации. Возможно, пользователь уже существует.")
        
        input("\nНажмите Enter для продолжения...")
    
    def logout(self):
        """Выход из системы"""
        self.api.logout()
        print("\n✅ Вы успешно вышли из системы")
        input("Нажмите Enter для продолжения...")
    
    def exit_program(self):
        """Выход из программы"""
        self.is_running = False
        self.api.close()
        print("\n👋 До свидания! Спасибо за использование нашей системы!")
        sys.exit(0)


def main():
    """Точка входа для консольного интерфейса"""
    ui = ConsoleUI()
    
    try:
        ui.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена пользователем")
        ui.api.close()
    except Exception as e:
        print(f"\n❌ Произошла ошибка: {e}")
        ui.api.close()
