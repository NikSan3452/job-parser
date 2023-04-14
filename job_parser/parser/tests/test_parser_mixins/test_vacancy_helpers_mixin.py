import datetime
from parser.forms import SearchingForm
from parser.mixins import VacancyHelpersMixin
from parser.models import City, FavouriteVacancy, HiddenCompanies, VacancyBlackList
from parser.tests.TestAssertions import Assertions

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages import get_messages
from django.db.models import QuerySet
from django.http import HttpRequest, QueryDict


@pytest.mark.django_db(transaction=True)
class TestVacancyHelpersMixin:
    """Класс описывает тестовые случаи для миксина VacancyHelpersMixin."""

    @pytest.mark.asyncio
    async def test_check_request_data(
        self, helpers_mixin: VacancyHelpersMixin, request_: HttpRequest
    ) -> None:
        """Тестирует метод удаления данных в запросе равных None или False.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин.
            request_ (HttpRequest): Запрос.
        """
        # Создаем объект QueryDict и имитируем запрос
        request_.GET = QueryDict("", mutable=True)
        request_.GET.update(
            {   
                "city": "None",
                "date_from": "2022-01-01",
                "date_to": "None",
                "title_search": "False",
                "experience": "None",
                "remote": "True",
                "job_board": "None",
            }
        )

        result = await helpers_mixin.check_request_data(request_)

        # Проверяем, что параметры с None или False были удалены из словаря
        expected = {"date_from": "2022-01-01", "remote": "True"}
        Assertions.assert_type(result, dict)
        Assertions.assert_compare_values(result, expected)

    @pytest.mark.asyncio
    async def test_check_vacancy_in_black_list(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        """Тестирует метод добавления вакансий в черный список.

        Args:
            helpers_mixin (VacancyHelpersMixin): Экземпляр VacancyHelpersMixin.
            request_ (HttpRequest): Запрос.
            test_user (User): Тестовый пользователь.
        """
        # Создаем фиктивные данные для теста
        vacancies = [
            {"url": "https://example.com/vacancy1"},
            {"url": "https://example.com/vacancy2"},
            {"url": "https://example.com/vacancy3"},
        ]

        request_.user = test_user

        # Добавляем вакансию в избранное
        await FavouriteVacancy.objects.acreate(
            user=test_user, url="https://example.com/vacancy2"
        )

        # Создаем запись в черном списке для вакансии 2
        await VacancyBlackList.objects.acreate(
            user=test_user, url="https://example.com/vacancy2"
        )

        # Проверяем, что вакансия 2 была удалена из списка
        result = await helpers_mixin.check_vacancy_in_black_list(vacancies, request_)
        expected = [
            {"url": "https://example.com/vacancy1"},
            {"url": "https://example.com/vacancy3"},
        ]
        Assertions.assert_type(result, list)
        Assertions.assert_compare_values(result, expected)

        # Проверяем, что вакансия 2 была удалена из избранного
        expected = await FavouriteVacancy.objects.filter(
            user=test_user, url="https://example.com/vacancy2"
        ).aexists()
        Assertions.assert_type(expected, bool)
        Assertions.assert_compare_values(False, expected)

        # Делаем пользователя анонимным и проверяем, что вернулся исходный список
        request_.user = AnonymousUser()
        result = await helpers_mixin.check_vacancy_in_black_list(vacancies, request_)
        Assertions.assert_compare_values(result, vacancies)

    @pytest.mark.asyncio
    async def test_check_company_in_hidden_list(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        # Создаем фиктивные данные для теста
        vacancies = [
            {"title": "vacancy1", "company": "test_company1"},
            {"title": "vacancy2", "company": "test_company2"},
            {"title": "vacancy3", "company": "test_company3"},
        ]

        request_.user = test_user

        # Создаем запись в списке скрытых компаний для test_company_2
        await HiddenCompanies.objects.acreate(user=test_user, name="test_company2")

        # Проверяем, что компания 2 была удалена из списка
        result = await helpers_mixin.check_company_in_hidden_list(vacancies, request_)
        expected = [
            {"title": "vacancy1", "company": "test_company1"},
            {"title": "vacancy3", "company": "test_company3"},
        ]
        Assertions.assert_type(result, list)
        Assertions.assert_compare_values(result, expected)

        # Делаем пользователя анонимным и проверяем, что вернулся исходный список
        request_.user = AnonymousUser()
        result = await helpers_mixin.check_company_in_hidden_list(vacancies, request_)
        Assertions.assert_compare_values(result, vacancies)

    @pytest.mark.asyncio
    async def test_get_favourite_vacancy(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        """Тестирует метод добавления вакансии в избранное.

        Args:
            helpers_mixin (VacancyHelpersMixin): Экземпляр VacancyHelpersMixin.
            request_ (HttpRequest): Запрос.
            test_user (User): Тестовый пользователь.
        """
        request_.user = test_user

        # Создаем фиктивные данные для теста
        url: str = "https://example.com/vacancy1"
        title: str = "Python"
        
        # Создаем запись в списке избранных вакансий
        await FavouriteVacancy.objects.acreate(user=test_user, url=url, title=title)

        # Проверяем что вакансия добавлена в избранное
        result = await helpers_mixin.get_favourite_vacancy(request_)
        Assertions.assert_type(result, QuerySet)
        for item in result:
            Assertions.assert_compare_values(item.url, url)

        # Делаем пользователя анонимным и проверяем, что вернулся пустой список
        request_.user = AnonymousUser()
        result = await helpers_mixin.get_favourite_vacancy(request_)
        vacancies: list = []
        Assertions.assert_compare_values(result, vacancies)

    @pytest.mark.asyncio
    async def test_get_pagination(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тестирует метод пагинации.

        Args:
            helpers_mixin (VacancyHelpersMixin): Экземпляр VacancyHelpersMixin.
            request_ (HttpRequest): Запрос.
        """
        # устанавливаем значение параметра "page" в словаре GET
        request_.GET = QueryDict("", mutable=True)
        request_.GET["page"] = 1

        # создаем список вакансий
        job_list: list[dict] = [
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4},
            {"id": 5},
            {"id": 6},
        ]

        # создаем пустой словарь для контекста
        context: dict = {}
        expected_list: list[dict] = [
            {"id": 1},
            {"id": 2},
            {"id": 3},
            {"id": 4},
            {"id": 5},
        ]  # Ожидаемое количество вакансий 5, т.к на странице отображается по 5 вакансий

        # Но общее количество вакансий 6
        expected_total_vacancies = 6

        # вызываем функцию get_pagination с передачей аргументов
        await helpers_mixin.get_pagination(request_, job_list, context)

        # Преобразуем объект Page в список перед сравнением
        # и проверяем что список объектов, а также общее количество
        # вакансий соответствуют ожидаемым значениям
        Assertions.assert_compare_values(
            list(context["object_list"]), expected_list
        )
        Assertions.assert_compare_values(
            context["total_vacancies"], expected_total_vacancies
        )
        # Проверка на пустой список
        empty_job_list: list = []
        empty_context: dict = {}
        await helpers_mixin.get_pagination(request_, empty_job_list, empty_context)
        Assertions.assert_compare_values(list(empty_context["object_list"]), [])
        Assertions.assert_compare_values(empty_context["total_vacancies"], 0)

    @pytest.mark.asyncio
    async def test_get_form_data(self, helpers_mixin: VacancyHelpersMixin) -> None:
        """Тестирует метод получения данных из формы.

        Args:
            helpers_mixin (VacancyHelpersMixin): Экземпляр VacancyHelpersMixin.
        """

        # Создаем форму с заполненными полями
        form = SearchingForm(
            {
                "city": "Москва",
                "job": "Developer",
                "date_from": "2022-01-01",
                "date_to": "2022-12-31",
                "title_search": True,
                "experience": 3,
                "remote": True,
                "job_board": "HeadHunter",
            }
        )

        assert form.is_valid()  # Проверяем валидность

        # Извлекаем данные из формы
        data = await helpers_mixin.get_form_data(form)
        expected = {
            "city": "москва",
            "job": "Developer",
            "date_from": datetime.date(2022, 1, 1),
            "date_to": datetime.date(2022, 12, 31),
            "title_search": True,
            "experience": 3,
            "remote": True,
            "job_board": "HeadHunter",
        }

        # Сравниваем фактический результат с ожидаемым
        Assertions.assert_type(data, dict)
        Assertions.assert_compare_values(data, expected)

    @pytest.mark.asyncio
    async def test_get_city_id(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тестирует метод получения id города из базы данных.

        Args:
            helpers_mixin (VacancyHelpersMixin): Экземпляр VacancyHelpersMixin.
            request_ (HttpRequest): Запрос.
        """
        request_.GET = QueryDict("", mutable=True)
        request_.GET["city"] = "Test City"
        # Создаем тестовый город в базе данных
        await City.objects.acreate(city="Test City", city_id="12345")

        # Проверяем, что функция возвращает правильный id города
        city_id = await helpers_mixin.get_city_id("Test City", request_)
        Assertions.assert_type(city_id, str)
        Assertions.assert_compare_values(city_id, "12345")

        # Проверяем, что функция возвращает None для несуществующего города
        city_id = await helpers_mixin.get_city_id("Nonexistent City", request_)
        Assertions.assert_type(city_id, None)
        Assertions.assert_compare_values(city_id, None)

        # Получаем сообщения Django
        messages = list(get_messages(request_))

        # Проверяем что сообщение для несуществующего города есть и выводится
        expected_message = "Город с таким названием отсутствует в базе"
        Assertions.assert_type(messages, list)
        Assertions.assert_compare_values(str(messages[0]), expected_message)
