import json

from django.db import DatabaseError, IntegrityError
from parser.models import VacancyBlackList

import pytest
from django.contrib.auth.models import User
from django.test import Client


@pytest.mark.django_db(transaction=True)
class TestAddVacancyToBlackListView:
    """Класс описывает тестовые случаи для представления AddVacancyToBlackListView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при добавлении
    вакансии в черный список: успешное добавление, добавление неавторизованным
    пользователем, добавление с невалидным JSON в запросе, добавление с отсутствующими
    обязательными полями, добавление с использованием неправильного HTTP-метода,
    обработка исключений при добавлении вакансии.
    """

    def test_add_vacancy_to_black_list_view(
        self, logged_in_client: Client, test_user: User, data: dict
    ) -> None:
        """Тест для проверки успешного добавления вакансии в черный список.

        В этом тесте отправляется POST-запрос на добавление вакансии в черный список
        и проверяется статус ответа. После этого проверяется, что объект
        `VacancyBlackList` был успешно создан в базе данных.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя для
            тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.post(
            "/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 200
        assert VacancyBlackList.objects.filter(
            user=test_user, url=data["url"], title=data["title"]
        ).exists()

    def test_add_vacancy_to_black_list_view_unauthenticated_user(
        self, client: Client, data: dict
    ) -> None:
        """Тест для проверки добавления вакансии в черный список неавторизованным
        пользователем.

        В этом тесте отправляется POST-запрос на добавление вакансии в черный список
        от имени неавторизованного пользователя. Проверяется статус ответа и URL
        перенаправления.

        Args:
            client (Client): Экземпляр клиента для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = client.post(
            "/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/add-to-black-list/"

    def test_add_vacancy_to_black_list_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки невалидного JSON в запросе.

        В этом тесте отправляется POST-запрос на добавление вакансии в черный список
        с невалидным JSON в теле запроса. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post(
            "/add-to-black-list/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_add_vacancy_to_black_list_view_missing_fields(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки отсутствия обязательных полей в запросе.

        В этом тесте отправляется POST-запрос на добавление вакансии в черный список
        без обязательных полей. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post("/add-to-black-list/", {})
        assert response.status_code == 400

    def test_add_vacancy_to_black_list_view_wrong_method(
        self, logged_in_client: Client, data: dict
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на добавление вакансии в черный список.
        Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get(
            "/add-to-black-list/",
            data=data,
        )
        assert response.status_code == 405

    def test_add_vacancy_to_black_list_view_exceptions(
        self, logged_in_client: Client, data: dict, mocker
    ) -> None:
        """Тест для проверки обработки исключений при добавлении вакансии в черный список.

        В этом тесте сначала создается заглушка (mock) для метода `aget_or_create`
        модели `VacancyBlackList`, которая вызывает исключение `IntegrityError`.
        Затем отправляется POST-запрос на добавление вакансии в черный список
        и проверяется статус ответа.

        После этого создается новая заглушка для метода `aget_or_create`,
        которая вызывает исключение `DatabaseError`.
        Затем снова отправляется POST-запрос на добавление вакансии в черный список
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
            mocker: Фикстура для создания заглушек (mocks) и подмены вызовов функций.
        """
        mocker.patch(
            "parser.models.VacancyBlackList.objects.aget_or_create",
            side_effect=IntegrityError,
        )
        response = logged_in_client.post(
            "/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500

        mocker.patch(
            "parser.models.VacancyBlackList.objects.aget_or_create",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}