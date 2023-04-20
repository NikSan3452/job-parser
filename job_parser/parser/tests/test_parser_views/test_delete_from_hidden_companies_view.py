import json
from parser.models import HiddenCompanies

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError, IntegrityError
from django.test import Client


@pytest.mark.django_db(transaction=True)
class TestDeleteFromHiddenCompaniesView:
    """Класс описывает тестовые случаи для представления DeleteFromHiddenCompaniesView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при удалении
    компании из списка скрытых: успешное удаление, удаление неавторизованным
    пользователем, удаление с невалидным JSON в запросе, удаление с отсутствующими
    обязательными полями, удаление с использованием неправильного HTTP-метода,
    обработка исключений при удалении компании.
    """

    def test_delete_from_hidden_companies_view(
        self, logged_in_client: Client, test_user: User
    ) -> None:
        """Тест для проверки успешного удаления компании из списка скрытых.

        В этом тесте сначала создается объект `HiddenCompanies` с данными.
        Затем отправляется POST-запрос на удаление компании из списка скрытых
        и проверяется статус ответа. После этого проверяется, что объект
        `HiddenCompanies` был успешно удален из базы данных.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя для
            тестирования.
        """
        HiddenCompanies.objects.create(user=test_user, name="Test company")
        response = logged_in_client.post(
            "/delete-from-hidden-companies/",
            data=json.dumps({"name": "Test company"}),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 200
        assert not HiddenCompanies.objects.filter(
            user=test_user, name="Test company"
        ).exists()

    def test_delete_from_hidden_companies_view_unauthenticated_user(
        self, client: Client
    ) -> None:
        """Тест для проверки попытки удаления компании из списка скрытых
        неавторизованным пользователем.

        В этом тесте отправляется POST-запрос на удаление компании из списка скрытых
        от имени неавторизованного пользователя и проверяется статус ответа и URL-адрес
        перенаправления.

        Args:
            client (Client): Фикстура, предоставляющая экземпляр клиента для
            тестирования.
        """
        response = client.post(
            "/delete-from-hidden-companies/",
            data=json.dumps({"name": "Test company"}),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/delete-from-hidden-companies/"

    def test_delete_from_hidden_companies_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки ошибки декодирования JSON при удалении компании
        из списка скрытых.

        В этом тесте отправляется POST-запрос с невалидным JSON на удаление компании
        из списка скрытых
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post(
            "/delete-from-hidden-companies/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_delete_from_hidden_companies_view_missing_fields(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки отсутствия обязательных полей при удалении
        компании из списка скрытых.

        В этом тесте отправляется POST-запрос без обязательных полей на удаление
        компании из списка скрытых
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post("/delete-from-hidden-companies/", {})
        assert response.status_code == 400

    def test_delete_from_hidden_companies_view_wrong_method(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода при удалении
        компании из списка скрытых.

        В этом тесте отправляется GET-запрос на удаление компании из списка скрытых
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.get(
            "/delete-from-hidden-companies/",
            data={"name": "Test company"},
        )
        assert response.status_code == 405

    def test_delete_from_hidden_companies_view_exceptions(
        self, logged_in_client: Client, mocker
    ) -> None:
        """Тест для проверки обработки исключений при удалении компании из списка
        скрытых.

        В этом тесте используется `mocker` для имитации исключений `IntegrityError`
        и `DatabaseError` при вызове метода `adelete` у объекта `HiddenCompanies`.
        После этого отправляется POST-запрос на удаление компании из списка скрытых
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            mocker: Фикстура для имитации поведения объектов.
        """
        mocker.patch(
            "parser.models.HiddenCompanies.objects.filter",
            side_effect=IntegrityError,
        )
        response = logged_in_client.post(
            "/delete-from-hidden-companies/",
            data=json.dumps({"name": "Test company"}),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500

        mocker.patch(
            "parser.models.HiddenCompanies.objects.filter",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/delete-from-hidden-companies/",
            data=json.dumps({"name": "Test company"}),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
