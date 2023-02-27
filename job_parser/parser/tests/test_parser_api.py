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

    def test_vacancy_list_method_get(self, mocker, client: Client) -> None:
        """Тестирует GET запросы к представлению списка вакансий."""
        mocker.patch(
            "parser.mixins.RedisCacheMixin.get_data_from_cache", return_value=[]
        )

        response = client.get(path="/list/")

        Assertions.assert_code_status(response, 200)
        Assertions.assert_object_in_response_context("form", response)
        Assertions.assert_object_in_response_context("object_list", response)
        Assertions.assert_object_in_response_context("list_favourite", response)

    @pytest.mark.parametrize(
        "job, city, date_from, date_to, experience, title_search, remote, job_board",
        [
            (
                "Python",
                "Москва",
                "2023-01-01",
                "2023-02-02",
                "0",
                False,
                False,
                "Не имеет значения",
            ),
            (
                "Python",
                "Москва",
                "2023-01-01",
                "2023-02-02",
                "1",
                True,
                True,
                "HeadHunter",
            ),
            ("Python", "", "2023-01-01", "2023-02-02", "2", False, False, "SuperJob"),
            ("Python", "", "", "", "1", False, False, "Zarplata"),
        ],
    )
    def test_vacancy_list_method_post(
        self,
        job: str,
        city: str | None,
        date_from: str | None,
        date_to: str | None,
        experience: str | None,
        title_search: str | None,
        remote: str | None,
        job_board: str | None,
        client: Client,
    ) -> None:
        """Тестирует POST запросы к представлению списка вакансий."""

        data = {
            "city": city,
            "job": job,
            "date_from": date_from,
            "date_to": date_to,
            "title_search": title_search,
            "experience": experience,
            "remote": remote,
            "job_board": job_board,
        }

        response = client.post(path="/list/", data=data)

        Assertions.assert_code_status(response, 200)
        Assertions.assert_compare_obj_and_response_obj(job, "job", response)
        Assertions.assert_compare_obj_and_response_obj(city, "city", response)
        Assertions.assert_compare_obj_and_response_obj(date_from, "date_from", response)
        Assertions.assert_compare_obj_and_response_obj(date_to, "date_to", response)
        Assertions.assert_compare_obj_and_response_obj(
            title_search, "title_search", response
        )
        Assertions.assert_compare_obj_and_response_obj(
            experience, "experience", response
        )
        Assertions.assert_compare_obj_and_response_obj(remote, "remote", response)
        Assertions.assert_compare_obj_and_response_obj(job_board, "job_board", response)
        Assertions.assert_object_in_response_context("form", response)
        Assertions.assert_object_in_response_context("object_list", response)
        Assertions.assert_object_in_response_context("list_favourite", response)

    def test_add_to_favourite_view(self) -> None:
        """Тестирует представление добавления вакансии в избранное."""
        data = {"url": self.vacancy_url, "title": self.vacancy_title}

        response = self.client.post(
            path="/favourite/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy_exists = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_add_vacancy_to_favorite(vacancy_exists)

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

        vacancy_exists = FavouriteVacancy.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_delete_vacancy_from_favourite(vacancy_exists)

    def test_add_to_black_list_view(self) -> None:
        """Тестирует представление добавления вакансии в черный список."""
        data = {"url": self.vacancy_url}

        response = self.client.post(
            path="/add-to-black-list/",
            data=json.dumps(data),
            content_type="application/json",
        )

        vacancy_exists = VacancyBlackList.objects.filter(
            user=self.user, url=self.vacancy_url
        ).exists()

        Assertions.assert_code_status(response, 200)
        Assertions.assert_add_vacancy_to_black_list(vacancy_exists)
