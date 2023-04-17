import json
from parser.models import HiddenCompanies

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError, IntegrityError
from django.test import Client


@pytest.fixture
def company_data() -> dict:
    """Фикстура для предоставления данных для отправки в запросе.

    Returns:
        dict: Словарь с данными для отправки в запросе.
    """
    vacancy_company = "Test Vacancy"
    data = {"company": vacancy_company}
    return data


@pytest.mark.django_db(transaction=True)
class TestHideCompanyView:
    """Класс описывает тестовые случаи для представления HideCompanyView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при скрытии вакансий
    компании: успешное скрытие, скрытие неавторизованным пользователем,
    скрытие с невалидным JSON в запросе, скрытие с отсутствующими обязательными полями,
    скрытие с использованием неправильного HTTP-метода, обработка исключений при скрытии
    компании.
    """

    def test_hide_company_view(
        self, logged_in_client: Client, test_user: User, company_data: dict
    ) -> None:
        """Тест для проверки успешного скрытия вакансий компании.

        В этом тесте отправляется POST-запрос на скрытие вакансий компании
        и проверяется статус ответа. После этого проверяется, что объект
        `HiddenCompanies` был успешно создан в базе данных.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя для
            тестирования.
            company_data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.post(
            "/hide-company/",
            data=json.dumps(company_data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 200
        assert HiddenCompanies.objects.filter(
            user=test_user, name=company_data["company"]
        ).exists()

    def test_hide_company_view_unauthenticated_user(
        self, client: Client, company_data: dict
    ) -> None:
        """Тест для проверки скрытия вакансий компании неавторизованным пользователем.

        В этом тесте отправляется POST-запрос на скрытие вакансий компании
        от имени неавторизованного пользователя. Проверяется статус ответа и URL
        перенаправления.

        Args:
            client (Client): Экземпляр клиента для тестирования.
            company_data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = client.post(
            "/hide-company/",
            data=json.dumps(company_data),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/hide-company/"

    def test_hide_company_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки невалидного JSON в запросе.

        В этом тесте отправляется POST-запрос на скрытие вакансий компании
        с невалидным JSON в теле запроса. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post(
            "/hide-company/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_hide_company_view_missing_fields(self, logged_in_client: Client) -> None:
        """Тест для проверки обработки отсутствия обязательных полей в запросе.

        В этом тесте отправляется POST-запрос на скрытие вакансий компании
        без обязательных полей. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post("/hide-company/", {})
        assert response.status_code == 400

    def test_hide_company_view_wrong_method(
        self, logged_in_client: Client, company_data: dict
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на скрытие вакансий компании.
        Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            company_data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get(
            "/hide-company/",
            data=company_data,
        )
        assert response.status_code == 405

    def test_hide_company_view_exceptions(
        self, logged_in_client: Client, company_data: dict, mocker
    ) -> None:
        """Тест для проверки обработки исключений при скрытии вакансий компании.

        В этом тесте сначала создается заглушка (mock) для метода `aget_or_create`
        модели `HiddenCompanies`, которая вызывает исключение `IntegrityError`.
        Затем отправляется POST-запрос на скрытие вакансий компании
        и проверяется статус ответа.

        После этого создается новая заглушка для метода `aget_or_create`,
        которая вызывает исключение `DatabaseError`.
        Затем снова отправляется POST-запрос на скрытие вакансий компании
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            company_data (dict): Фикстура, предоставляющая данные для отправки в запросе.
            mocker: Фикстура для создания заглушек (mocks) и подмены вызовов функций.
        """
        mocker.patch(
            "parser.models.HiddenCompanies.objects.aget_or_create",
            side_effect=IntegrityError,
        )
        response = logged_in_client.post(
            "/hide-company/",
            data=json.dumps(company_data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500

        mocker.patch(
            "parser.models.HiddenCompanies.objects.aget_or_create",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/hide-company/",
            data=json.dumps(company_data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
