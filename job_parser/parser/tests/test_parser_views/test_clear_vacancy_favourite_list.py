from parser.models import FavouriteVacancy

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import Client
from pytest_mock import MockFixture


@pytest.mark.django_db(transaction=True)
class TestClearVacancyFavouriteListPositive:
    """
    Класс описывает позитивные тестовые случаи для представления
    ClearVacancyFavouriteList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки успешного выполнения операции очистки
    списка избранных вакансий для аутентифицированного пользователя.
    """

    def test_clear_vacancy_favourite_list_success(
        self, logged_in_client: Client, test_user: User
    ) -> None:
        """
        Тест для проверки успешного выполнения операции очистки списка избранных
        вакансий для аутентифицированного пользователя.

        В этом тесте создаются записи избранных вакансий для тестового пользователя,
        затем отправляется POST-запрос на очистку списка избранных вакансий.
        После этого проверяется статус ответа и отсутствие записей избранных вакансий
        для тестового пользователя.


        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя.
        """
        # Создание записей избранных вакансий для тестового пользователя
        FavouriteVacancy.objects.create(
            user=test_user, url="https://example.com/1", title="Test 1"
        )
        FavouriteVacancy.objects.create(
            user=test_user, url="https://example.com/2", title="Test 2"
        )

        # Отправка POST-запроса на очистку списка избранных вакансий
        response = logged_in_client.post("/clear-favourite-list/")
        assert response.status_code == 200
        assert response.json() == {"status": "Список избранных вакансий успешно очищен"}

        # Проверка, что список избранных вакансий пуст
        assert not FavouriteVacancy.objects.filter(user=test_user).exists()


@pytest.mark.django_db(transaction=True)
class TestClearVacancyFavouriteListNegative:
    """
    Класс описывает негативные тестовые случаи для представления
    ClearVacancyFavouriteList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки обработки ошибок при выполнении операции
    очистки списка избранных вакансий:
    - попытка выполнения операции для неаутентифицированного пользователя и
    обработка исключения DatabaseError.
    """

    def test_clear_vacancy_favourite_list_unauthenticated_user(
        self, client: Client
    ) -> None:
        """
        Тест для проверки попытки выполнения операции очистки списка избранных вакансий
        для неаутентифицированного пользователя.

        В этом тесте отправляется POST-запрос на очистку списка избранных вакансий
        без предварительной аутентификации пользователя. После этого проверяется статус
        ответа и URL перенаправления.


        Args:
            client (Client): Фикстура, предоставляющая экземпляр клиента Django.
        """
        # Отправка POST-запроса на очистку списка избранных вакансий для
        # неаутентифицированного пользователя
        response = client.post("/clear-favourite-list/")
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/clear-favourite-list/"

    def test_clear_vacancy_to_favourites_wrong_method(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на очистку списка избранных вакансий,
        хотя представление обрабатывает только POST-запросы.
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get("/clear-favourite-list/")
        assert response.status_code == 405

    def test_clear_vacancy_favourite_list_exceptions(
        self, logged_in_client: Client, mocker: MockFixture
    ) -> None:
        """
        Тест для проверки обработки исключения DatabaseError при выполнении операции
        очистки списка избранных вакансий.

        В этом тесте используется библиотека `mocker` для имитации вызова исключения
        `DatabaseError` при попытке удаления записей избранных вакансий.
        Затем отправляется POST-запрос на очистку списка избранных вакансий.
        После этого проверяется статус ответа и сообщение об ошибке.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            mocker (MockFixture): Фикстура для имитации вызова исключений.
        """

        # Проверка вызова исключения DatabaseError
        mocker.patch(
            "parser.models.FavouriteVacancy.objects.filter",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post("/clear-favourite-list/")
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
