from typing import Any
import pytest
from django.contrib.auth.models import User


@pytest.fixture
def fix_user(db: Any) -> User:
    """Фикстура создающая тестового пользователя.

    Args:
        db (Any): Фикстура pytest-django, отвечает за подключение
        к тестовой базе данных.

    Returns:
        User: Тестовый пользователь.
    """
    test_user = User.objects.create(username="testuser", password="testpass")
    return test_user