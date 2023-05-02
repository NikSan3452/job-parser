import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import Client
from pytest_mock import MockFixture

from parser.models import VacancyBlackList


@pytest.mark.django_db(transaction=True)
class TestClearVacancyBlackListPositive:
    """
    Класс описывает позитивные тестовые случаи для представления ClearVacancyBlackList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки успешного выполнения операции очистки
    черного списка вакансий для аутентифицированного пользователя.
    """

    def test_clear_vacancy_black_list_success(
        self, logged_in_client: Client, test_user: User
    ) -> None:
        """
        Тест для проверки успешного выполнения операции очистки черного списка
        вакансий для аутентифицированного пользователя.

        В этом тесте создаются записи черного списка вакансий для тестового пользователя,
        затем отправляется POST-запрос на очистку черного списка вакансий.
        После этого проверяется статус ответа и отсутствие записей черного списка вакансий
        для тестового пользователя.


        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя.
        """
        # Создание записей черного списка вакансий для тестового пользователя
        VacancyBlackList.objects.create(
            user=test_user, url="https://example.com/1", title="Test 1"
        )
        VacancyBlackList.objects.create(
            user=test_user, url="https://example.com/2", title="Test 2"
        )

        # Отправка POST-запроса на очистку черного списка вакансий
        response = logged_in_client.post("/clear-blacklist-list/")
        assert response.status_code == 200
        assert response.json() == {"status": "Черный список вакансий успешно очищен"}

        # Проверка, что черный список вакансий пуст
        assert not VacancyBlackList.objects.filter(user=test_user).exists()


@pytest.mark.django_db(transaction=True)
class TestClearVacancyBlackListNegative:
    """
    Класс описывает негативные тестовые случаи для представления ClearVacancyBlackList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки обработки исключения DatabaseError
    при выполнении операции очистки черного списка вакансий.
    """

    def test_clear_vacancy_black_list_unauthenticated_user(
        self, client: Client, data: dict
    ) -> None:
        """Тест для проверки очистки черного списка неавторизованным
        пользователем.

        В этом тесте отправляется POST-запрос на очистку черного списка
        от имени неавторизованного пользователя. Проверяется статус ответа и URL
        перенаправления.

        Args:
            client (Client): Экземпляр клиента для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = client.post("/clear-blacklist-list/")
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/clear-blacklist-list/"

    def test_clear_vacancy_black_list_wrong_method(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на очистку черного списка.
        Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get("/clear-blacklist-list/")
        assert response.status_code == 405

    def test_clear_vacancy_black_list_exceptions(
        self, logged_in_client: Client, mocker: MockFixture
    ) -> None:
        """
        Тест для проверки обработки исключения DatabaseError при выполнении операции
        очистки черного списка вакансий.

        В этом тесте используется библиотека `mocker` для имитации вызова исключения
        `DatabaseError` при попытке удаления записей черного списка вакансий.
        Затем отправляется POST-запрос на очистку черного списка.
        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            mocker (MockFixture): Фикстура для имитации вызова исключений.
        """

        # Проверка вызова исключения DatabaseError
        mocker.patch(
            "parser.models.VacancyBlackList.objects.filter",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post("/clear-blacklist-list/")
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
