import json
from parser.models import FavouriteVacancy

import pytest
from django.contrib.auth.models import User
from django.db import DatabaseError
from django.test import Client


@pytest.mark.django_db(transaction=True)
class TestDeleteVacancyFromFavouritesView:
    """
    Класс описывает тестовые случаи для представления DeleteVacancyFromFavouritesView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при удалении
    вакансии из избранного: успешное удаление, удаление неавторизованным пользователем,
    удаление с невалидным JSON в запросе, удаление с отсутствующими обязательными полями,
    удаление с использованием неправильного HTTP-метода, удаление несуществующей вакансии,
    обработка исключений при удалении вакансии.
    """

    def test_delete_vacancy_from_favourites_view(
        self, logged_in_client: Client, test_user: User, data: dict
    ) -> None:
        """Тест для проверки успешного удаления вакансии из избранного.

        В этом тесте сначала создается объект `FavouriteVacancy` с данными из
        фикстуры `data`.
        Затем отправляется POST-запрос на удаление вакансии из избранного
        и проверяется статус ответа.
        После этого проверяется, что объект `FavouriteVacancy` был успешно
        удален из базы данных.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        FavouriteVacancy.objects.create(user=test_user, **data)
        response = logged_in_client.post(
            "/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 200
        assert not FavouriteVacancy.objects.filter(
            user=test_user, url=data["url"]
        ).exists()

    def test_delete_vacancy_from_favourites_view_unauthenticated_user(
        self, client: Client, data: dict
    ) -> None:
        """Тест для проверки удаления вакансии из избранного неавторизованным
        пользователем.

        В этом тесте отправляется POST-запрос на удаление вакансии из избранного
        от имени неавторизованного пользователя. Проверяется статус ответа и URL
        перенаправления.

        Args:
            client (Client): Экземпляр клиента для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = client.post(
            "/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/delete-favourite/"

    def test_delete_vacancy_from_favourites_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки невалидного JSON в запросе.

        В этом тесте отправляется POST-запрос на удаление вакансии из избранного
        с невалидным JSON в теле запроса. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post(
            "/delete-favourite/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_delete_vacancy_from_favourites_view_missing_fields(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки отсутствия обязательных полей в запросе.

        В этом тесте отправляется POST-запрос на удаление вакансии из избранного
        с неполными данными (только URL без заголовка).
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post("/delete-favourite/", {})
        assert response.status_code == 400

    def test_delete_vacancy_from_favourites_view_wrong_method(
        self, logged_in_client: Client, data: dict
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода.

        В этом тесте отправляется GET-запрос на удаление вакансии из избранного,
        хотя представление обрабатывает только POST-запросы.
        После этого проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get(
            "/delete-favourite/",
            data=data,
        )
        assert response.status_code == 405

    def test_delete_vacancy_from_favourites_view_not_found(
        self, logged_in_client: Client, data: dict
    ) -> None:
        """Тест для проверки удаления несуществующей вакансии.

        В этом тесте отправляется POST-запрос на удаление вакансии из избранного,
        которой нет в базе данных. Проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.post(
            "/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 404

    def test_delete_vacancy_from_favourites_view_exceptions(
        self, logged_in_client: Client, data: dict, mocker
    ) -> None:
        """Тест для проверки обработки исключений при удалении вакансии из избранного.

        В этом тесте создается заглушка (mock) для метода `filter`
        модели `FavouriteVacancy`, которая вызывает исключение `DatabaseError`.
        Затем отправляется POST-запрос на удаление вакансии из избранного
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
            mocker: Фикстура для создания заглушек (mocks) и подмены вызовов функций.
        """
        mocker.patch(
            "parser.models.FavouriteVacancy.objects.filter",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
