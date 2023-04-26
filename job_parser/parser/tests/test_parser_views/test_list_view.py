import datetime
from parser.api import main
from parser.forms import SearchingForm
from parser.mixins import RedisCacheMixin
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList
from parser.tests.TestAssertions import Assertions
from parser.views import VacancyListView
from typing import Awaitable

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.http import HttpRequest, QueryDict


@pytest.mark.django_db(transaction=True)
class TestVacancyListView:
    """Класс описывает тестовые случаи для представления списка вакансий."""

    def setup_method(self) -> list[dict]:
        """Создает тестовые данные.
        Returns:
            list[dict]: Тестовые данные.
        """
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
                "job_board": "HeadHunter",
                "title": "ruby",
                "url": "http://example.com/vacancy3",
                "description": "описание",
                "company": "company3",
                "published_at": datetime.date.today(),
                "experience": "Без опыта",
            },
            {
                "job_board": "Zarplata",
                "title": "C++",
                "url": "http://example.com/vacancy4",
                "description": "описание",
                "company": "company4",
                "published_at": datetime.date.today(),
                "experience": "Без опыта",
            },
        ]

        return data

    async def mock_vacancies_from_scraper(
        self, request_: HttpRequest, params: dict
    ) -> list[dict]:
        """Mock - метод, имитирует возвращаемое значение для
        метода vacancies_from_scraper.

        Args:
            request_ (HttpRequest): Запрос.
            params (dict): Параметры запроса.

        Returns:
            list[dict]: Тестовые данные.
        """
        return_value = self.setup_method()
        return [return_value[0]]

    async def mock_main_run(self, form_params: dict) -> list[dict]:
        """Mock - метод, имитирует возвращаемое значение для
        метода main.run().

        Args:
            params (dict): Параметры запроса.

        Returns:
            list[dict]: Тестовые данные.
        """
        return_value = self.setup_method()
        return return_value

    @pytest.fixture
    async def set_cache(
        self, cache_key: RedisCacheMixin, redis_mixin: RedisCacheMixin
    ) -> None:
        """Фикстура добавляет данные в кэш.

        Args:
            cache_key (RedisCacheMixin): Кэш - ключ.
            redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.
        Returns:
            None
        """
        data = self.setup_method()
        return await redis_mixin.set_data_to_cache(data)

    @pytest.mark.asyncio
    async def test_get_anonymous(
        self, request_: HttpRequest, set_cache: Awaitable
    ) -> None:
        """Тестирует метод GET представления списка вакансий
        от имени анонимного пользователя.

        Args:
            request_ (HttpRequest): Запрос.
            set_cache (Awaitable): Фикстура, добавляет данные в кэш.
        """
        # Добавляем тестовые данные в кэш.
        await set_cache

        # Тестовые данные
        data = self.setup_method()

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
        assert response.status_code == 200
        assert "form" in response.context_data
        assert data[0]["title"] in object_list[0]["title"]
        assert data[1]["title"] in object_list[1]["title"]
        assert data[2]["title"] in object_list[2]["title"]

    @pytest.mark.asyncio
    async def test_get_authenticated(
        self,
        request_: HttpRequest,
        test_user: User,
        set_cache: Awaitable,
    ) -> None:
        """Тестирует метод GET представления списка вакансий
        от имени аутентифицированного пользователя.

        Args:
            request_ (HttpRequest): Запрос.
            test_user (User): Тестовый пользователь.
            set_cache (Awaitable): Фикстура, добавляет данные в кэш.
        """
        # Тестовые данные
        data = self.setup_method()

        # Добавляем тестовые данные в кэш.
        await set_cache

        # Вызов представления
        view = VacancyListView.as_view()

        # Создаем запись в списке избранных вакансий
        await FavouriteVacancy.objects.acreate(
            user=test_user, url=data[0]["url"], title=data[0]["title"]
        )

        # Создаем запись в списке скрытых компаний для company2
        await HiddenCompanies.objects.acreate(user=test_user, name=data[1]["company"])

        # Создаем запись в черном списке для вакансии 3
        await VacancyBlackList.objects.acreate(user=test_user, url=data[2]["url"])

        # Если пользователь вошел в систему
        request_.user = test_user
        response = await view(request_)
        response.render()

        # Получаем список избранного
        qs_favourite = response.context_data["list_favourite"].filter(user=test_user)
        favourite = [fav.url for fav in qs_favourite]

        # Получаем общий список с вакансиями
        object_list = list(response.context_data["object_list"])

        # Проверяем, что код ответа верный и тело ответа содержит вакансии
        # добавленные в избранное
        assert response.status_code == 200
        assert data[0]["url"] in favourite

        # Проверяем, что тело ответа не содержит вакансии скрытой компании
        assert data[1]["title"] not in object_list[0]["title"]

        # Проверяем, что тело ответа не содержит вакансии добавленной в черный список
        assert data[2]["url"] not in object_list[0]["url"]

        # Проверяем, что форма присутствует в контексте
        assert "form" in response.context_data

    @pytest.mark.asyncio
    async def test_post_anonymous(
        self,
        request_: HttpRequest,
        monkeypatch,
    ) -> None:
        """Тестирует метод  POST представления списка вакансий
        от имени анонимного пользователя.

        Args:
            request_ (HttpRequest): Запрос.
            monkeypatch (_type_): Фикстура для фиктивных запросов.
        """
        # Тестовые данные
        data = self.setup_method()

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
            VacancyListView,
            "get_vacancies_from_scraper",
            self.mock_vacancies_from_scraper,
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
        assert response.status_code == 200

        # Проверяем, что общий список содержит только вакансии из скрапера
        assert data[1]["job_board"] not in object_list[0]["job_board"]

        # Проверяем, что форма присутствует в контексте
        assert "form" in response.context_data

    @pytest.mark.asyncio
    async def test_post_authenticated(
        self,
        request_: HttpRequest,
        test_user: User,
        monkeypatch,
    ) -> None:
        """Тестирует метод  POST представления списка вакансий
        от имени аутентифицированного пользователя.

        Args:
            request_ (HttpRequest): Запрос.
            test_user (User): Тестовый пользователь.
            monkeypatch (_type_): Фикстура для фиктивных запросов.
        """
        # Тестовые данные
        data = self.setup_method()

        # Добавляем путь в запрос
        request_.path = "/list/"
        # Меняем метод запроса
        request_.method = "POST"

        # Делаем пользователя анонимным
        request_.user = test_user

        # Заполняем форму данными
        params = {
            "job": "ruby",
            "city": "москва",
            "date_from": "2022-01-01",
            "date_to": "2023-12-31",
            "title_search": False,
            "experience": 1,
            "remote": False,
            "job_board": "HeadHunter",
        }

        form = SearchingForm(params)
        if form.is_valid():
            # Добавляем параметры в запрос
            request_.POST = QueryDict("", mutable=True)
            request_.POST.update(form.cleaned_data)

        # Создаем запись в списке избранных вакансий
        await FavouriteVacancy.objects.acreate(
            user=test_user, url=data[1]["url"], title=data[1]["title"]
        )

        # Создаем запись в списке скрытых компаний для company2
        await HiddenCompanies.objects.acreate(user=test_user, name=data[2]["company"])

        # Создаем запись в черном списке для вакансии 3
        await VacancyBlackList.objects.acreate(user=test_user, url=data[3]["url"])

        # Имитируем метод получения вакансий из API
        monkeypatch.setattr(main, "run", self.mock_main_run)

        # Вызываем представление
        view = VacancyListView.as_view()
        response = await view(request_)
        response.render()

        # Получаем вакансии из API
        await main.run(params)

        # Получаем список избранного
        qs_favourite = response.context_data["list_favourite"].filter(user=test_user)
        favourite = [fav.url for fav in qs_favourite]

        # Получаем общий список с вакансиями
        object_list = list(response.context_data["object_list"])

        # Проверяем, что код ответа верный и тело содержит вакансии 
        # добавленные в избранное
        assert response.status_code == 200
        assert data[1]["url"] in favourite

        # Проверяем, что тело ответа не содержит вакансии скрытой компании
        assert data[2]["title"]not in object_list[0]["title"]

        # Проверяем, что тело ответа не содержит вакансии добавленной в черный список
        assert data[3]["url"] not in object_list[0]["url"]

        # Проверяем, что форма присутствует в контексте
        assert "form" in response.context_data
