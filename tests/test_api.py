"""
Тесты для API библиотеки
"""
import pytest
from src.api.library_api import LibraryAPI
from src.models.user import UserRole


@pytest.fixture
def library_api():
    """Фикстура для API библиотеки"""
    api = LibraryAPI()
    yield api
    api.close()


class TestLibraryAPI:
    """Тесты для LibraryAPI"""
    
    def test_register_and_login(self, library_api):
        """Тест регистрации и входа пользователя"""
        # Регистрация
        user = library_api.register(
            username="newuser",
            email="newuser@example.com",
            password="password123",
            full_name="Новый Пользователь",
            phone="+79990001122"
        )
        
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "Новый Пользователь"
        assert user.role == UserRole.READER
        
        # Вход
        logged_in_user = library_api.login("newuser", "password123")
        assert logged_in_user is not None
        assert logged_in_user.username == "newuser"
        
        # Проверка текущего пользователя
        current_user = library_api.get_current_user()
        assert current_user is not None
        assert current_user.username == "newuser"
    
    def test_login_wrong_password(self, library_api):
        """Тест входа с неверным паролем"""
        # Сначала регистрируем пользователя
        library_api.register(
            username="testuser",
            email="test@example.com",
            password="correct_password",
            full_name="Тест"
        )
        
        # Пробуем войти с неверным паролем
        user = library_api.login("testuser", "wrong_password")
        assert user is None
    
    def test_search_books_empty(self, library_api):
        """Тест поиска книг (пустая база)"""
        books = library_api.search_books("Гарри Поттер")
        assert isinstance(books, list)
        assert len(books) == 0
    
    def test_admin_add_book(self, library_api):
        """Тест добавления книги администратором"""
        # Регистрируем администратора
        # В реальном API нужно добавить метод для создания админа
        # Пока просто проверяем, что без прав нельзя добавлять
        
        # Попытка добавить книгу без входа
        book = library_api.add_new_book(
            title="Новая книга",
            author="Автор",
            year=2024,
            isbn="123-456-789",
            publisher="Издательство",
            genre="Жанр",
            pages=200,
            quantity=5
        )
        
        assert book is None  # Не должно получиться без прав админа
    
    def test_logout(self, library_api):
        """Тест выхода из системы"""
        # Регистрируем и входим
        library_api.register(
            username="logoutuser",
            email="logout@example.com",
            password="pass",
            full_name="Выходящий"
        )
        library_api.login("logoutuser", "pass")
        
        # Проверяем, что вошли
        assert library_api.get_current_user() is not None
        
        # Выходим
        library_api.logout()
        
        # Проверяем, что вышли
        assert library_api.get_current_user() is None
