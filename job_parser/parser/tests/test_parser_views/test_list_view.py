import datetime
from parser.forms import SearchingForm
from parser.mixins import RedisCacheMixin
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList
from parser.tests.TestAssertions import Assertions
from parser.views import VacancyListView
from typing import Awaitable

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest, QueryDict


@pytest.fixture
def test_data() -> list[dict]:
    """Фикстура создает тестовые данные и добавляет их в кэш.

    Args:
        cache_key (RedisCacheMixin): Кэш-ключ.
        redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.

    Returns:
        list[dict]: Тестовые данные.
    """
    # Создаем тестовые данные
    data = [
        {
            "job_board": "Habr career",
            "title": "python",
            "url": "http://example.com/vacancy1",
            "description": "описание",
            "company": "company1",
            "published_at": datetime.date.today(),
            "experience": "Без опыта",
        },
        {
            "job_board": "SuperJob",
            "title": "java",
            "url": "http://example.com/vacancy2",
            "description": "описание",
            "company": "company2",
            "published_at": datetime.date.today(),
            "experience": "Без опыта",
        },
        {
            "job_board": "Headhunter",
            "title": "ruby",
            "url": "http://example.com/vacancy3",
            "description": "описание",
            "company": "company3",
            "published_at": datetime.date.today(),
            "experience": "Без опыта",
        },
    ]

    return data


@pytest.fixture
async def set_cache(
    cache_key: RedisCacheMixin, redis_mixin: RedisCacheMixin, test_data: list[dict]
) -> Awaitable:

    return await redis_mixin.set_data_to_cache(test_data)


@pytest.mark.django_db(transaction=True)
class TestVacancyListView:
    """Класс описывает тестовые случаи для представления списка вакансий."""

    @pytest.mark.asyncio
    async def test_get_anonymous(
        self,
        request_: HttpRequest,
        test_user: User,
        set_cache: Awaitable,
        test_data: list[dict],
    ) -> None:
        """Тестирует метод GET представления списка вакансий
        от имени анонимного пользователя.

        Args:
            request_ (HttpRequest): Запрос.
            test_user (User): Тестовый пользователь.
            test_data (Awaitable): Тестовые данные.
        """
        # Добавляем тестовые данные в кэш.
        await set_cache

        # Добавляем путь в запрос
        request_.path = "/list/"

        # Делаем пользователя анонимным
        request_.user = AnonymousUser()

        # Экземпляр представления
        view = VacancyListView.as_view()
        response = await view(request_)
        response.render()

        # Получаем общий список с вакансиями
        object_list = list(response.context_data["object_list"])

        # Проверяем, что код ответа верный и тело ответа содержит установленные данные
        Assertions.assert_status_code(response, 200)
        Assertions.assert_value_in_obj("form", response.context_data)
        Assertions.assert_value_in_obj(test_data[0]["title"], object_list[0]["title"])
        Assertions.assert_value_in_obj(test_data[1]["title"], object_list[1]["title"])
        Assertions.assert_value_in_obj(test_data[2]["title"], object_list[2]["title"])

    @pytest.mark.asyncio
    async def test_get_authenticated(
        self,
        request_: HttpRequest,
        test_user: User,
        set_cache: Awaitable,
        test_data: list[dict],
    ) -> None:
        # Добавляем тестовые данные в кэш.
        await set_cache

        view = VacancyListView.as_view()

        # Создаем запись в списке избранных вакансий
        await FavouriteVacancy.objects.acreate(
            user=test_user, url=test_data[0]["url"], title=test_data[0]["title"]
        )

        # Создаем запись в списке скрытых компаний для company2
        await HiddenCompanies.objects.acreate(
            user=test_user, name=test_data[1]["company"]
        )

        # Создаем запись в черном списке для вакансии 3
        await VacancyBlackList.objects.acreate(user=test_user, url=test_data[2]["url"])

        # Если пользователь вошел в систему
        request_.user = test_user
        response = await view(request_)
        response.render()

        # Получаем список избранного
        qs_favourite = response.context_data["list_favourite"].filter(user=test_user)
        favourite = [fav.title for fav in qs_favourite]

        # Получаем общий список с вакансиями
        object_list = list(response.context_data["object_list"])

        # Проверяем, что код ответа верный и тело ответа содержит вакансии добавленные в избранное
        Assertions.assert_status_code(response, 200)
        Assertions.assert_value_in_obj(test_data[0]["title"], favourite)

        # Проверяем, что тело ответа не содержит вакансии скрытой компании
        Assertions.assert_value_not_in_obj(
            test_data[1]["title"], object_list[0]["title"]
        )

        # Проверяем, что тело ответа не содержит вакансии добавленной в черный список
        Assertions.assert_value_not_in_obj(test_data[2]["url"], object_list[0]["url"])

        # Проверяем, что форма присуствует в контексте
        Assertions.assert_value_in_obj("form", response.context_data)

    async def mock_run(self, request_, params):
        return_value = [
            {
                "job_board": "Habr career",
                "title": "python",
                "url": "http://example.com/vacancy1",
                "description": "описание",
                "company": "company1",
                "published_at": datetime.date.today(),
                "experience": "Без опыта",
            },
            {
                "job_board": "SuperJob",
                "title": "java",
                "url": "http://example.com/vacancy2",
                "description": "описание",
                "company": "company2",
                "published_at": datetime.date.today(),
                "experience": "Без опыта",
            },
            {
                "job_board": "Headhunter",
                "title": "ruby",
                "url": "http://example.com/vacancy3",
                "description": "описание",
                "company": "company3",
                "published_at": datetime.date.today(),
                "experience": "Без опыта",
            },
        ]

        return return_value

    @pytest.mark.asyncio
    async def test_post_anonymous(
        self,
        request_: HttpRequest,
        test_user: User,
        set_cache: Awaitable,
        test_data: list[dict],
        monkeypatch,
    ) -> None:

        # Добавляем путь в запрос
        request_.path = "/list/"
        # Меняем метод запроса
        request_.method = "POST"

        # Делаем пользователя анонимным
        request_.user = AnonymousUser()

        # Заполняем форму данными
        params = {
            "job": "python",
            "city": "москва",
            "date_from": "2022-01-01",
            "date_to": "2023-12-31",
            "title_search": False,
            "experience": 1,
            "remote": False,
            "job_board": "Habr career",
        }

        form = SearchingForm(params)
        if form.is_valid():
            # Добавляем параметры в запрос
            request_.POST = QueryDict("", mutable=True)
            request_.POST.update(form.cleaned_data)

        # Имитируем метод получения вакансий из скрапера
        monkeypatch.setattr(
            VacancyListView, "get_vacancies_from_scraper", self.mock_run
        )

        # Вызываем представление
        view = VacancyListView.as_view()
        response = await view(request_)
        response.render()

        # Экземпляр представления
        view_instance = VacancyListView()
        # Получаем вакансии из скрапера
        await view_instance.get_vacancies_from_scraper(request_, params)

        # Получаем общий список с вакансиями
        object_list = list(response.context_data["object_list"])
        # Проверяем, что код ответа верный и тело ответа содержит установленные данные
        Assertions.assert_status_code(response, 200)
        
