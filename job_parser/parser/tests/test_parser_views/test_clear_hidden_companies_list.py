import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import Client
from pytest_mock import MockFixture

from parser.models import HiddenCompanies


@pytest.mark.django_db(transaction=True)
class TestClearHiddenCompaniesListPositive:
    """
    Класс описывает позитивные тестовые случаи для представления
    ClearHiddenCompaniesList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки успешного выполнения операции очистки
    списка скрытых компаний для аутентифицированного пользователя.
    """

    def test_clear_hidden_companies_list_success(
        self, logged_in_client: Client, test_user: User
    ) -> None:
        """
        Тест для проверки успешного выполнения операции очистки списка скрытых компаний
        для аутентифицированного пользователя.

        В этом тесте создаются записи списка скрытых компаний для тестового
        пользователя, затем отправляется POST-запрос на очистку списка скрытых компаний.
        После этого проверяется статус ответа и отсутствие записей списка скрытых
        компаний для тестового пользователя.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя.
        """
        # Создание записей списка скрытых компаний для тестового пользователя
        HiddenCompanies.objects.create(user=test_user, name="company1")
        HiddenCompanies.objects.create(user=test_user, name="company2")

        # Отправка POST-запроса на очистку списка скрытых компаний
        response = logged_in_client.post("/clear-hidden-companies-list/")

        # Проверка статуса ответа и отсутствия записей списка скрытых компаний
        assert response.status_code == 200
        assert response.json() == {"status": "Список скрытых компаний успешно очищен"}
        assert not HiddenCompanies.objects.filter(user=test_user).exists()


@pytest.mark.django_db(transaction=True)
class TestClearHiddenCompaniesListNegative:
    """
    Класс описывает негативные тестовые случаи для представления
    ClearHiddenCompaniesList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки обработки исключения DatabaseError
    при выполнении операции очистки списка скрытых компаний.
    """

    def test_delete_from_hidden_companies_view_unauthenticated_user(
        self, client: Client
    ) -> None:
        """Тест для проверки попытки очистки списка скрытых компаний
        неавторизованным пользователем.

        В этом тесте отправляется POST-запрос на очистку списка скрытых компаний
        от имени неавторизованного пользователя и проверяется статус ответа и URL-адрес
        перенаправления.

        Args:
            client (Client): Фикстура, предоставляющая экземпляр клиента для
            тестирования.
        """
        response = client.post("/clear-hidden-companies-list/")
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/clear-hidden-companies-list/"

    def test_clear_hidden_companies_list_wrong_method(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на очистку списка скрытых компаний,
        хотя представление обрабатывает только POST-запросы.
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get("/clear-hidden-companies-list/")
        assert response.status_code == 405

    def test_clear_hidden_companies_list_exceptions(
        self, logged_in_client: Client, mocker: MockFixture
    ) -> None:
        """
        Тест для проверки обработки исключения DatabaseError при выполнении операции
        очистки списка скрытых компаний.

        В этом тесте используется библиотека `mocker` для имитации вызова исключения
        `DatabaseError` при попытке удаления записей списка скрытых компаний.
        Затем отправляется POST-запрос на очистку списка скрытых компаний.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            mocker (MockFixture): Фикстура для имитации вызова исключений.
        """
        # Проверка вызова исключения DatabaseError
        mocker.patch(
            "parser.models.HiddenCompanies.objects.filter",
            side_effect=DatabaseError,
        )

        # Отправка POST-запроса на очистку списка скрытых компаний
        response = logged_in_client.post("/clear-hidden-companies-list/")

        # Проверка статуса ответа и содержимого тела ответа
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
