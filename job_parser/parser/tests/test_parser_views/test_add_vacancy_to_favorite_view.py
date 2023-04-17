import json
from parser.models import FavouriteVacancy

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError, IntegrityError
from django.test import Client


@pytest.mark.django_db(transaction=True)
class TestAddVacancyToFavouritesView:
    """
    Класс описывает тестовые случаи для представления AddVacancyToFavouritesView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при добавлении
    вакансии в избранное: успешное добавление, добавление неавторизованным пользователем,
    добавление с невалидным JSON в запросе, добавление с отсутствующими обязательными
    полями, добавление с использованием неправильного HTTP-метода,
    обработка исключений при добавлении вакансии.
    """

    def test_add_vacancy_to_favourites_view(
        self, logged_in_client: Client, test_user: User, data: dict
    ) -> None:
        """Тест для проверки добавления вакансии в избранное аутентифицированным
        пользователем.

        В этом тесте выполняется аутентификация пользователя с помощью метода
        `force_login`, затем отправляется POST-запрос на добавление вакансии
        в избранное.
        После этого проверяется статус ответа и наличие добавленной вакансии
        в избранном.


        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя.
            data (dict): Словарь с данными для теста.
        """
        # Отправка POST-запроса на представление AddVacancyToFavouritesView
        response = logged_in_client.post(
            "/favourite/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )

        # Проверка ответа и создания объекта FavouriteVacancy
        assert response.status_code == 200
        assert FavouriteVacancy.objects.filter(
            user=test_user, url=data["url"], title=data["title"]
        ).exists()

    def test_add_vacancy_to_favourites_view_unauthenticated_user(
        self, client: Client, data: dict
    ) -> None:
        """Тест для проверки добавления вакансии в избранное
        неаутентифицированным пользователем.

        В этом тесте отправляется POST-запрос на добавление вакансии в избранное
        без аутентификации пользователя.
        После этого проверяется статус ответа и URL перенаправления.


        Args:
            client (Client): Фикстура, предоставляющая экземпляр клиента Django
            для выполнения запросов.
            data (dict): Фикстура, предоставляющая экземпляр пользователя.
        """
        response = client.post(
            "/favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/favourite/"

    def test_add_vacancy_to_favourites_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки невалидного JSON при добавлении вакансии
        в избранное.

        В этом тесте отправляется POST-запрос на добавление вакансии в избранное
        с невалидным JSON в теле запроса.
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
        """
        # Отправка POST-запроса с невалидным JSON
        response = logged_in_client.post(
            "/favourite/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_add_vacancy_to_favourites_view_missing_fields(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки неполных данных при добавлении вакансии
        в избранное.

        В этом тесте отправляется POST-запрос на добавление вакансии в избранное
        с неполными данными (только URL без заголовка).
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр
            клиента Django c аутентифицированным пользователем.
        """
        # Отправка POST-запроса с неполными данными
        response = logged_in_client.post("/favourite/", {"url": "https://example.com"})
        assert response.status_code == 400

    def test_add_vacancy_to_favourites_view_wrong_method(
        self, logged_in_client: Client, data: dict
    ) -> None:
        """Тест для проверки обработки неправильного HTTP-метода при добавлении
        вакансии в избранное.

        В этом тесте отправляется GET-запрос на добавление вакансии в избранное,
        хотя представление обрабатывает только POST-запросы.
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get(
            "/favourite/",
            data=data,
        )
        assert response.status_code == 405

    def test_add_vacancy_to_favourites_view_exceptions(
        self, logged_in_client: Client, data: dict, mocker
    ) -> None:
        """Тест для проверки обработки исключений при добавлении вакансии в избранное.

        В этом тесте сначала создается заглушка (mock) для метода `aget_or_create`
        модели `FavouriteVacancy`, которая вызывает исключение `IntegrityError`.
        Затем отправляется POST-запрос на добавление вакансии в избранное
        и проверяется статус ответа, а также содержимое ответа в формате JSON.

        После этого создается новая заглушка для метода `aget_or_create`,
        которая вызывает исключение `DatabaseError`.
        Затем снова отправляется POST-запрос на добавление вакансии в избранное
        и проверяется статус ответа, а также содержимое ответа в формате JSON.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
            mocker: Фикстура для создания заглушек (mocks) и подмены вызовов функций.
        """
        # Проверка вызова исключения IntegrityError
        mocker.patch(
            "parser.models.FavouriteVacancy.objects.aget_or_create",
            side_effect=IntegrityError,
        )
        response = logged_in_client.post(
            "/favourite/",
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 400
        assert response.json() == {"Ошибка": "Такая вакансия уже есть в избранном"}

        # Проверка вызова исключения Exception
        mocker.patch(
            "parser.models.FavouriteVacancy.objects.aget_or_create",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/favourite/",
            data=data,
            content_type="application/json",
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
