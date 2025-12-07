"""
Веб-интерфейс для системы каталога на Flask
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from ...api.library_api import LibraryAPI
import json


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # В реальном проекте используйте переменные окружения

# Глобальный объект API (в реальном проекте используйте контекст приложения)
api = LibraryAPI()


@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/api/login', methods=['POST'])
def login():
    """API для входа в систему"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = api.login(username, password)
    
    if user:
        # Сохраняем информацию о пользователе в сессии
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role.value
        
        return jsonify({
            'success': True,
            'user': user.to_dict()
        })
    
    return jsonify({'success': False, 'error': 'Неверные учетные данные'})


@app.route('/api/books/search', methods=['GET'])
def search_books():
    """API для поиска книг"""
    query = request.args.get('q', '')
    author = request.args.get('author', '')
    year = request.args.get('year', '')
    genre = request.args.get('genre', '')
    
    filters = {}
    if author:
        filters['author'] = author
    if year and year.isdigit():
        filters['year'] = int(year)
    if genre:
        filters['genre'] = genre
    
    books = api.search_books(query, **filters)
    
    return jsonify({
        'success': True,
        'books': [book.to_dict() for book in books]
    })


@app.route('/api/books/reserve', methods=['POST'])
def reserve_book():
    """API для бронирования книги"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    data = request.json
    book_id = data.get('book_id')
    
    if not book_id:
        return jsonify({'success': False, 'error': 'Не указан ID книги'})
    
    reservation = api.reserve_book(int(book_id))
    
    if reservation:
        return jsonify({
            'success': True,
            'reservation': reservation.to_dict()
        })
    
    return jsonify({'success': False, 'error': 'Ошибка бронирования'})


@app.route('/api/user/reservations', methods=['GET'])
def get_user_reservations():
    """API для получения бронирований пользователя"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Требуется авторизация'})
    
    reservations = api.get_my_reservations()
    
    return jsonify({
        'success': True,
        'reservations': [r.to_dict() for r in reservations]
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000)
