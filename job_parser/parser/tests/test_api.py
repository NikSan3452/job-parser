import json
import pytest

from typing import Callable
from django.test import Client
from django.contrib.auth import get_user_model
from parser.models import FavouriteVacancy, VacancyBlackList
from assertions import Assertions

BASE_URL: str = "http://127.0.0.1:8000"
POSITIVE_STATUS_CODE: int = 200


@pytest.mark.django_db
class TestHomePage:
    def test_get_homepage(self, client: Client) -> None:
        response = client.get(path=f"{BASE_URL}")
        assert response.status_code == POSITIVE_STATUS_CODE


@pytest.mark.django_db
class TestVacancyListPage:

    vacancy_url: str = "https://example.com/vacancy"
    vacancy_title: str = "Example title"

    client: Client = Client()
    User: Callable[..., User] = get_user_model()

    def setup_method(self) -> None:
        self.user = self.User.objects.create_user(
            username="testuser", password="testpass"
        )
        self.client.force_login(self.user)

    def test_add_to_favourite_view(self) -> None:
        data = {"url": self.vacancy_url, "title": self.vacancy_title}

        response = self.client.post(
            path=f"{BASE_URL}/favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, POSITIVE_STATUS_CODE)
        Assertions.assert_add_vacancy_to_favorite(vacancy)

    def test_delete_from_favourite_view(self) -> None:
        data = {"url": self.vacancy_url}

        FavouriteVacancy.objects.create(
            user=self.user, url=self.vacancy_url, title=self.vacancy_title
        )

        response = self.client.post(
            path=f"{BASE_URL}/delete-favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, POSITIVE_STATUS_CODE)
        Assertions.assert_delete_vacancy_from_favourite(vacancy)

    def test_add_to_black_list_view(self) -> None:
        data = {"url": self.vacancy_url}

        response = self.client.post(
            path=f"{BASE_URL}/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy = VacancyBlackList.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, POSITIVE_STATUS_CODE)
        Assertions.assert_add_vacancy_to_black_list(vacancy)
