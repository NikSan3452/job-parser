import json

import pytest
from parser.models import VacancyBlackList

from django.contrib.auth.models import User
from django.db import DatabaseError, IntegrityError
from django.test import Client

@pytest.mark.django_db(transaction=True)
class TestDeleteVacancyFromBlacklistView:
    """Класс описывает тестовые случаи для представления DeleteVacancyFromBlacklistView.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.

    Этот класс содержит тесты для проверки различных сценариев при удалении
    вакансии из черного списка: успешное удаление, удаление неавторизованным
    пользователем, удаление с невалидным JSON в запросе, удаление с отсутствующими
    обязательными полями, удаление с использованием неправильного HTTP-метода,
    обработка исключений при удалении вакансии.
    """

    def test_delete_vacancy_from_black_list_view(
        self, logged_in_client: Client, test_user: User, data: dict
    ) -> None:
        """Тест для проверки успешного удаления вакансии из черного списка.

        В этом тесте сначала создается объект `FavouriteVacancy` с данными из
        фикстуры `data`.
        Затем отправляется POST-запрос на удаление вакансии из черного списка
        и проверяется статус ответа. После этого проверяется, что объект
        `VacancyBlackList` был успешно удален из базы данных.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            test_user (User): Фикстура, предоставляющая экземпляр пользователя для
            тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        VacancyBlackList.objects.create(user=test_user, **data)
        response = logged_in_client.post(
            "/delete-from-blacklist/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 200
        assert not VacancyBlackList.objects.filter(
            user=test_user, url=data["url"]
        ).exists()

    def test_delete_vacancy_from_black_list_view_unauthenticated_user(
        self, client: Client, data: dict
    ) -> None:
        """Тест для проверки попытки удаления вакансии из черного списка
        неавторизованным пользователем.

        В этом тесте отправляется POST-запрос на удаление вакансии из черного списка
        от имени неавторизованного пользователя и проверяется статус ответа и URL-адрес
        перенаправления.

        Args:
            client (Client): Фикстура, предоставляющая экземпляр клиента для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = client.post(
            "/delete-from-blacklist/",
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 302
        assert response.url == "/accounts/login/?next=/delete-from-blacklist/"

    def test_delete_vacancy_from_black_list_view_json_decode_error(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки ошибки декодирования JSON при удалении вакансии
        из черного списка.

        В этом тесте отправляется POST-запрос с невалидным JSON на удаление вакансии
        из черного списка
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post(
            "/delete-from-blacklist/",
            data="invalid_json",
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_delete_vacancy_from_black_list_view_missing_fields(
        self, logged_in_client: Client
    ) -> None:
        """Тест для проверки обработки отсутствия обязательных полей при удалении
        вакансии из черного списка.

        В этом тесте отправляется POST-запрос без обязательных полей на удаление
        вакансии из черного списка
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
        """
        response = logged_in_client.post("/delete-from-blacklist/", {})
        assert response.status_code == 400

    def test_delete_vacancy_from_black_list_view_wrong_method(
        self, logged_in_client: Client, data: dict
    ) -> None:
        """Тест для проверки использования неправильного HTTP-метода при удалении
        вакансии из черного списка.

        В этом тесте отправляется GET-запрос на удаление вакансии из черного списка
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
        """
        response = logged_in_client.get(
            "/delete-from-blacklist/",
            data=data,
        )
        assert response.status_code == 405

    def test_delete_vacancy_from_black_list_view_exceptions(
        self, logged_in_client: Client, data: dict, mocker
    ) -> None:
        """Тест для проверки обработки исключений при удалении вакансии
        из черного списка.

        В этом тесте используется `mocker` для имитации исключений `IntegrityError`
        и `DatabaseError` при вызове метода `adelete` у объекта `VacancyBlackList`.
        После этого отправляется POST-запрос на удаление вакансии из черного списка
        и проверяется статус ответа.

        Args:
            logged_in_client (Client): Фикстура, предоставляющая экземпляр пользователя
            для тестирования.
            data (dict): Фикстура, предоставляющая данные для отправки в запросе.
            mocker: Фикстура для имитации поведения объектов.
        """
        mocker.patch(
            "parser.models.VacancyBlackList.objects.filter",
            side_effect=IntegrityError,
        )
        response = logged_in_client.post(
            "/delete-from-blacklist/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500

        mocker.patch(
            "parser.models.VacancyBlackList.objects.filter",
            side_effect=DatabaseError,
        )
        response = logged_in_client.post(
            "/delete-from-blacklist/",
            data=json.dumps(data),
            content_type="application/json",
            follow=True,
        )
        assert response.status_code == 500
        assert response.json() == {"Ошибка": "Произошла ошибка базы данных"}
