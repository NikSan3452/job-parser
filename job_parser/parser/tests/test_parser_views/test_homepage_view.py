import pytest
from django.http import HttpRequest

from parser.forms import SearchingForm
from parser.views import HomePageView


@pytest.mark.django_db(transaction=True)
class TestHomePageView:
    """Класс описывает тестовые случаи для представления домашней страницы."""

    def setup_method(self) -> HomePageView:
        self.view = HomePageView()
        return self.view

    def test_home_page_view_get_request(self, request_: HttpRequest) -> None:
        """Тестирует возвращаемый status code представления домашней страницы.

        Args:
            request_ (HttpRequest): Запрос.
        """
        self.view.setup(request_)
        response = self.view.get(request_)
        assert response.status_code == 200

    def test_home_page_view_redirect(self, request_: HttpRequest) -> None:
        """Тестирует редирект после отправки формы с представления
        домашней страницы

        Args:
            request_ (HttpRequest): Запрос.
        """
        data = dict(
            job="Python",
            city="Москва",
            date_from="2023-01-01",
            date_to="2023-02-02",
            experience="0",
            title_search=False,
            remote=False,
            job_board="Не имеет значения",
        )
        form = SearchingForm(data=data)
        self.view.request = request_
        response = self.view.form_valid(form)

        assert form.is_valid() is True
        assert response.status_code == 302
