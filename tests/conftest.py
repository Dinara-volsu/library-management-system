"""
Конфигурация pytest
"""
import pytest
import sys
import os

# Добавляем src в путь импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Настройка тестовой среды"""
    # Можно добавить код для подготовки тестовой среды
    yield
    # И код для очистки после тестов
