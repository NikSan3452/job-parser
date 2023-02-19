import json
import pytest

from django.test import Client
from django.contrib.auth.models import User
from parser.models import FavouriteVacancy, VacancyBlackList
from django.test import Client
from assertions import Assertions


@pytest.mark.django_db
class TestHomePage:
    def test_get_homepage(self, client: Client) -> None:
        """Тестирует домашнюю страницу.

        Args:
            client (Client): Клиент.
        """
        response = client.get(path="/")
        assert response.status_code == 200


@pytest.mark.django_db
class TestVacancyListPage:

    vacancy_url: str = "https://example.com/vacancy"
    vacancy_title: str = "Example title"

    client: Client = Client()

    def setup_method(self) -> None:
        """Создает тестового пользователя и входит под ним."""
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.force_login(self.user)

    def test_vacancy_list_method_get(self, mocker):
        """Тестирует GET запросы к представлению списка вакансий."""
        mocker.patch(
            "parser.mixins.VacancyHelpersMixin.get_data_from_cache", return_value=[]
        )

        client = Client()
        response = client.get(path="/list/")

        assert response.status_code == 200
        assert "form" in response.context
        assert "object_list" in response.context
        assert "list_favourite" in response.context

    def test_vacancy_list_method_post(self):
        """Тестирует POST запросы к представлению списка вакансий."""
        client = Client()
        data = {
            "city": "Москва",
            "job": "Python",
            "date_from": "2022-01-01",
            "date_to": "2022-01-31",
            "title_search": "Python",
            "experience": "0",
            "remote": False,
        }

        response = client.post(path="/list/", data=data)

        assert response.status_code == 200
        assert "city" in response.context
        assert "date_from" in response.context
        assert "date_to" in response.context
        assert "title_search" in response.context
        assert "experience" in response.context
        assert "remote" in response.context
        assert "form" in response.context
        assert "object_list" in response.context
        assert "list_favourite" in response.context

    def test_add_to_favourite_view(self) -> None:
        """Тестирует представление добавления вакансии в избранное."""
        data = {"url": self.vacancy_url, "title": self.vacancy_title}

        response = self.client.post(
            path="/favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_add_vacancy_to_favorite(vacancy)

    def test_delete_from_favourite_view(self) -> None:
        """Тестирует представление удаления вакансии из избранного."""
        data = {"url": self.vacancy_url}

        FavouriteVacancy.objects.create(
            user=self.user, url=self.vacancy_url, title=self.vacancy_title
        )

        response = self.client.post(
            path="/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_delete_vacancy_from_favourite(vacancy)

    def test_add_to_black_list_view(self) -> None:
        """Тестирует представление добавления вакансии в черный список."""
        data = {"url": self.vacancy_url}

        response = self.client.post(
            path="/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = VacancyBlackList.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_add_vacancy_to_black_list(vacancy)
