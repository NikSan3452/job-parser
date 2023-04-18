import asyncio
from parser.mixins import RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin
from typing import Any, Generator

import pytest
from django.contrib.auth.models import User
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory


def add_middleware_to_request(request: HttpRequest) -> HttpRequest:
    """Добавляет middleware.

    Args:
        request (HttpRequest): Запрос.

    Returns:
        HttpRequest: Запрос с включенными middleware.
    """
    # Добавляем middleware для сессий
    middleware = SessionMiddleware(lambda req: HttpResponse())
    middleware.process_request(request)
    request.session.save()

    # Добавляем middleware для сообщений
    middleware = MessageMiddleware(lambda req: HttpResponse())
    middleware.process_request(request)
    request._messages = FallbackStorage(request)
    return request


@pytest.fixture
def request_() -> HttpRequest:
    """Фикстура для создания фиктивных запросов.
    Returns:
        HttpRequest: Запрос.
    """
    request = RequestFactory().get("/")

    request = add_middleware_to_request(request)
    return request


@pytest.fixture
def helpers_mixin() -> VacancyHelpersMixin:
    """Фикстура добавляющая экземпляр VacancyHelpersMixin.

    Returns:
        VacancyHelpersMixin: экземпляр VacancyHelpersMixin.
    """
    return VacancyHelpersMixin()


@pytest.fixture
def cache_key(redis_mixin: RedisCacheMixin, request_: HttpRequest) -> str:
    """Фикстура создающая кэш-ключ для Redis.

    Args:
        redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.
        request_ (HttpRequest): Запрос.

    Returns:
        str: кэш-ключ
    """
    loop = asyncio.get_event_loop()
    cache_key = loop.run_until_complete(redis_mixin.create_cache_key(request_))
    return cache_key


@pytest.fixture
def redis_mixin() -> RedisCacheMixin:
    """Фикстура добавляющая экземпляр RedisCacheMixin.

    Returns:
        VacancyHelpersMixin: экземпляр RedisCacheMixin.
    """
    return RedisCacheMixin()


@pytest.fixture()
def scraper_mixin() -> VacancyScraperMixin:
    """Фикстура добавляющая экземпляр VacancyScraperMixin.

    Returns:
        VacancyHelpersMixin: экземпляр VacancyScraperMixin.
    """
    return VacancyScraperMixin()


@pytest.fixture
def test_user(db: Any) -> User:
    """Фикстура создающая тестового пользователя.

    Args:
        db (Any): Фикстура pytest-django, отвечает за подключение
        к тестовой базе данных.

    Returns:
        User: Тестовый пользователь.
    """
    test_user = User.objects.create(username="testuser", password="testpass")
    return test_user


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker) -> Generator:
    """
    Фикстура, чистит оставшиеся соединения, которые могут зависать
    из потоков или внешних процессов. Расширение pytest_django.django_db_setup
    """

    yield

    with django_db_blocker.unblock():
        from django.db import connections

        conn = connections["default"]
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM pg_stat_activity;""")
        print("current connections")
        for r in cursor.fetchall():
            print(r)

        terminate_sql = (
            """
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '%s'
                AND pid <> pg_backend_pid();
        """
            % conn.settings_dict["NAME"]
        )
        print("Terminate SQL: ", terminate_sql)
        cursor.execute(terminate_sql)


@pytest.fixture
def data() -> dict:
    """Фикстура для предоставления данных для отправки в запросе.

    Returns:
        dict: Словарь с данными для отправки в запросе.
    """
    vacancy_url = "https://example.com/vacancy/1"
    vacancy_title = "Test Vacancy"
    data = {"url": vacancy_url, "title": vacancy_title}
    return data


@pytest.fixture
def logged_in_client(client: Client, test_user: User) -> Client:
    """Фикстура для предоставления экземпляра пользователя для тестирования.

    Args:
        client (Client): Экземпляр клиента для тестирования.
        test_user (User): Экземпляр пользователя для тестирования.

    Returns:
        Client: Экземпляр клиента с авторизованным пользователем.
    """
    client.force_login(test_user)
    return client
