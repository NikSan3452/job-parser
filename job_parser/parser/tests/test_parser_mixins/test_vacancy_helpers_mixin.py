import datetime

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.contrib.messages import get_messages
from django.db.models import QuerySet
from django.http import HttpRequest, QueryDict
from django.test import Client
from pytest_mock import MockerFixture

from parser.forms import SearchingForm
from parser.mixins import VacancyHelpersMixin
from parser.models import City, FavouriteVacancy, HiddenCompanies, VacancyBlackList


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckRequestDataPositive:
    """Класс описывает позитивные тестовые случаи для проверки данных запроса.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при проверке
    данных запроса:
    возможность получения данных из запроса, проверка соответствия полученных данных
    ожидаемым значениям.
    """

    async def test_check_request_data(
        self, helpers_mixin: VacancyHelpersMixin, client: Client
    ) -> None:
        """Тест проверяет получение данных из запроса.

        Отправляется GET-запрос с указанными параметрами.
        Ожидается, что результат вызова метода `check_request_data` будет
        соответствовать ожидаемому значению.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            client (Client): Клиент для отправки запросов.
        """
        response = client.get(
            "/",
            {
                "city": "None",
                "date_from": "2022-01-01",
                "date_to": "None",
                "title_search": "False",
                "experience": "None",
                "remote": "True",
                "job_board": "None",
            },
        )
        result = await helpers_mixin.check_request_data(response.wsgi_request)
        expected = {"date_from": "2022-01-01", "remote": "True"}
        assert isinstance(result, dict)
        assert result == expected


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckRequestDataNegative:
    """Класс описывает негативные тестовые случаи для проверки данных запроса.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при проверке
    данных запроса:
    проверка поведения метода `check_request_data` при передаче невалидного значения.
    """

    async def test_check_request_data_invalid_request(
        self, helpers_mixin: VacancyHelpersMixin
    ) -> None:
        """Тест проверяет поведение метода `check_request_data` при передаче
        невалидного значения.

        Вызывается метод `check_request_data` с передачей значения `None`.
        Ожидается, что результат вызова метода будет равен `None`.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин со вспомогательными методами.
        """
        result = await helpers_mixin.check_request_data(None)
        assert result is None


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckVacancyInBlackListPositive:
    """Класс описывает позитивные тестовые случаи для проверки наличия вакансий
    в черном списке.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при проверке
    вакансий в черном списке:
    проверка удаления вакансии из списка, проверка удаления вакансии из избранного,
    проверка поведения метода `check_vacancy_in_black_list` при анонимном пользователе.
    """

    async def test_check_vacancy_in_black_list(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        """Тест проверяет наличие вакансии в черном списке.

        Создается список вакансий и одна из них добавляется в избранное и черный список.
        Вызывается метод `check_vacancy_in_black_list` с передачей списка вакансий и
        запроса.
        Ожидается, что результат вызова метода будет соответствовать ожидаемому значению
        (без вакансии из черного списка).
        Проверяется, что вакансия была удалена из избранного.
        Проверяется поведение метода при анонимном пользователе.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            test_user (User): Фикстура для создания тестового пользователя.
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
        assert isinstance(result, list)
        assert result == expected

        # Проверяем, что вакансия 2 была удалена из избранного
        expected = await FavouriteVacancy.objects.filter(
            user=test_user, url="https://example.com/vacancy2"
        ).aexists()
        assert isinstance(expected, bool)
        assert False is expected

        # Делаем пользователя анонимным и проверяем, что вернулся исходный список
        request_.user = AnonymousUser()
        result = await helpers_mixin.check_vacancy_in_black_list(vacancies, request_)
        assert result == vacancies


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckVacancyInBlackListNegative:
    """Класс описывает негативные тестовые случаи для проверки вакансий в черном списке.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при проверке
    вакансий в черном списке:
    проверка поведения метода `check_vacancy_in_black_list` при ошибке базы данных.
    """

    async def test_check_vacancy_in_black_list_exception(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        mocker: MockerFixture,
    ) -> None:
        """Тест проверяет поведение метода `check_vacancy_in_black_list` при ошибке
        базы данных.

        Используется мок-объект для имитации ошибки базы данных.
        Вызывается метод `check_vacancy_in_black_list` с передачей пустого списка
        вакансий и запроса.
        Ожидается, что результат вызова метода будет равен пустому списку.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            mocker (MockerFixture): Фикстура для создания мок-объектов.
        """
        mock_filter = mocker.patch("parser.models.VacancyBlackList.objects.filter")
        mock_filter.side_effect = Exception("database error")
        result = await helpers_mixin.check_vacancy_in_black_list([], request_)
        assert result == []


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckCompanyInHiddenListPositive:
    """Класс описывает позитивные тестовые случаи для проверки компании в списке
    скрытых.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при проверке
    компании в списке скрытых:
    проверка удаления вакансии из списка, проверка поведения метода
    `check_company_in_hidden_list` при анонимном пользователе.
    """

    async def test_check_company_in_hidden_list(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        """Тест проверяет наличие компании в списке скрытых.

        Создается список вакансий и компания из одной из них добавляется в список
        скрытых.
        Вызывается метод `check_company_in_hidden_list` с передачей списка вакансий и
        запроса.
        Ожидается, что результат вызова метода будет соответствовать ожидаемому значению
        (без вакансии из списка скрытых).
        Проверяется поведение метода при анонимном пользователе.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            test_user (User): Фикстура для создания тестового пользователя.
        """
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
        assert isinstance(result, list)
        assert result == expected

        # Делаем пользователя анонимным и проверяем, что вернулся исходный список
        request_.user = AnonymousUser()
        result = await helpers_mixin.check_company_in_hidden_list(vacancies, request_)
        assert result == vacancies


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestCheckCompanyInHiddenListNegative:
    """Класс описывает негативные тестовые случаи для проверки компаний в скрытом списке.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при проверке
    компаний в скрытом списке:
    проверка поведения метода `check_company_in_hidden_list` при ошибке базы данных.
    """

    async def test_check_company_in_hidden_list_exception(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        mocker: MockerFixture,
    ):
        """Тест проверяет поведение метода `check_company_in_hidden_list` при ошибке
        базы данных.

        Используется мок-объект для имитации ошибки базы данных.
        Вызывается метод `check_company_in_hidden_list` с передачей пустого списка
        вакансий и запроса.
        Ожидается, что результат вызова метода будет равен пустому списку.

        Args:
            mocker (MockerFixture): Фикстура для создания мок-объектов.
        """
        mock_filter = mocker.patch("parser.models.VacancyBlackList.objects.filter")
        mock_filter.side_effect = Exception("database error")
        result = await helpers_mixin.check_company_in_hidden_list([], request_)
        assert result == []


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetFavouriteVacancyPositive:
    """Класс описывает позитивные тестовые случаи для получения списка избранных
    вакансий.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при получении
    списка избранных вакансий пользователя.
    """

    async def test_get_favourite_vacancy(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        test_user: User,
    ) -> None:
        """Тест проверяет получение списка избранных вакансий пользователя.

        Создается запись в списке избранных вакансий для тестового пользователя.
        Ожидается, что при вызове метода `get_favourite_vacancy` будет возвращен список
        избранных вакансий пользователя.
        После этого пользователь делается анонимным и ожидается, что при вызове метода
        `get_favourite_vacancy` будет возвращен пустой список.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            test_user (User): Фикстура для создания тестового пользователя.
        """
        request_.user = test_user

        # Создаем фиктивные данные для теста
        url: str = "https://example.com/vacancy1"
        title: str = "Python"

        # Создаем запись в списке избранных вакансий
        await FavouriteVacancy.objects.acreate(user=test_user, url=url, title=title)

        # Проверяем что вакансия добавлена в избранное
        result = await helpers_mixin.get_favourite_vacancy(request_)
        assert isinstance(result, QuerySet)
        for item in result:
            assert item.url == url

        # Делаем пользователя анонимным и проверяем, что вернулся пустой список
        request_.user = AnonymousUser()
        result = await helpers_mixin.get_favourite_vacancy(request_)
        vacancies: list = []
        assert result == vacancies


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetFavouriteVacancyNegative:
    """Класс описывает негативные тестовые случаи для получения списка избранных вакансий.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при получении
    списка избранных вакансий пользователя.
    """

    async def test_get_favourite_vacancy_exception(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        mocker: MockerFixture,
    ) -> None:
        """Тест проверяет обработку исключения при получении списка избранных вакансий.

        Используется мок-объект для имитации исключения при вызове метода `filter`
        менеджера модели FavouriteVacancy.
        Ожидается, что при вызове метода `get_favourite_vacancy` будет возвращен пустой
        список.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин со вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            mocker (MockerFixture): Фикстура для создания мок-объектов.
        """
        mock_filter = mocker.patch("parser.models.FavouriteVacancy.objects.filter")
        mock_filter.side_effect = Exception("database error")
        result = await helpers_mixin.get_favourite_vacancy(request_)
        assert result == []


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetPaginationPositive:
    """Класс описывает позитивные тестовые случаи для метода get_pagination.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при вызове
    метода get_pagination: проверка корректной обработки списка вакансий и возврата
    ожидаемых значений в контексте, проверка обработки пустого списка вакансий.
    """

    async def test_get_pagination(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тест проверяет корректную обработку списка вакансий методом get_pagination.

        Создается фиктивный объект запроса с помощью фикстуры request_ и устанавливается
        значение параметра "page" в словаре GET. Создается список вакансий и пустой
        словарь для контекста. Вызывается метод get_pagination с передачей аргументов и
        проверяется, что в контексте есть ключ "object_list" и его значение
        соответствует ожидаемому списку вакансий. Также проверяется, что в контексте
        есть ключ "total_vacancies" и его значение равно общему количеству вакансий.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин со вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
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
        assert list(context["object_list"]), expected_list
        assert context["total_vacancies"] == expected_total_vacancies
        # Проверка на пустой список
        empty_job_list: list = []
        empty_context: dict = {}
        await helpers_mixin.get_pagination(request_, empty_job_list, empty_context)
        assert list(empty_context["object_list"]) == []
        assert empty_context["total_vacancies"] == 0


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetPaginationNegative:
    """Класс описывает негативные тестовые случаи для метода get_pagination.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при вызове
    метода get_pagination: проверка обработки неправильного номера страницы.
    """

    async def test_get_pagination_invalid_page_number(
        request_: HttpRequest, helpers_mixin: VacancyHelpersMixin
    ):
        """Тест проверяет обработку неправильного номера страницы.

        Создается фиктивный объект запроса с помощью фикстуры request_ и устанавливается
        значение параметра "page" в словаре GET равным строке "invalid_page_number".
        Создается фиктивный список работ и пустой словарь для контекста.
        Вызывается метод get_pagination с передачей аргументов и проверяется, что в
        контексте есть ключ "object_list" и его значение равно первой странице
        пагинатора.

        Args:
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            helpers_mixin (VacancyHelpersMixin): Миксин со вспомогательными методами.
        """
        request_.GET = QueryDict("page=invalid_page_number")
        # Создаем фиктивный список вакансий
        job_list = [{"id": 1}, {"id": 2}]
        # Создаем фиктивный контекст
        context = {}
        # Вызываем метод get_pagination с фиктивными данными
        await helpers_mixin.get_pagination(request_, job_list, context)
        # Проверяем, что в контексте есть ключ "object_list" и его значение равно
        # первой странице пагинатора
        assert "object_list" in context
        assert list(context["object_list"]) == job_list[:5]


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetFormDataPositive:
    """Класс описывает позитивные тестовые случаи для получения данных из формы поиска
    вакансий.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки корректности извлечения данных из формы
    поиска вакансий.
    """

    async def test_get_form_data(self, helpers_mixin: VacancyHelpersMixin) -> None:
        """Тест проверяет корректность извлечения данных из формы поиска вакансий.

        Создается форма с заполненными полями и проверяется ее валидность.
        Извлекаются данные из формы и сравниваются с ожидаемыми значениями.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
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
        assert isinstance(data, dict)
        assert data == expected


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetFormDataNegative:
    """Класс описывает негативные тестовые случаи для получения данных из формы поиска
    вакансий.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки корректности обработки невалидных форм и
    форм с некорректными данными.
    """

    async def test_get_form_data_invalid_form(
        self, helpers_mixin: VacancyHelpersMixin
    ) -> None:
        """Тест проверяет обработку невалидной формы.

        Создается пустая форма и проверяется ее невалидность.
        Попытка извлечения данных из формы должна вернуть None.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
        """
        form = SearchingForm({})
        assert not form.is_valid()
        data = await helpers_mixin.get_form_data(form)
        assert data is None

    async def test_get_form_data_wrong_data_type(
        self, helpers_mixin: VacancyHelpersMixin
    ) -> None:
        """Тест проверяет обработку формы с некорректными типами данных.

        Создается форма с некорректными типами данных и проверяется ее невалидность.
        Попытка извлечения данных из формы должна вернуть None.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
        """
        form = SearchingForm(
            {
                "city": 123,
                "job": 123,
                "date_from": "wrong_type",
                "date_to": "wrong_type",
                "title_search": "wrong_type",
                "experience": "wrong_type",
                "remote": "wrong_type",
                "job_board": 123,
            }
        )
        assert not form.is_valid()
        data = await helpers_mixin.get_form_data(form)
        assert data is None


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetCityIdPositive:
    """Класс описывает позитивные тестовые случаи для метода get_city_id.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при вызове
    метода get_city_id из класса VacancyHelpersMixin:
    проверка возвращаемого значения при передаче существующего города
    """

    async def test_get_city_id_existing_city(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тест проверяет возвращаемое значение при передаче существующего города.

        Вызывается метод get_city_id с передачей существующего города.
        Ожидается, что возвращаемое значение будет равно 12345.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
        """
        request_.GET = QueryDict("", mutable=True)
        request_.GET["city"] = "Test City"
        # Проверяем, что функция возвращает правильный id города
        await City.objects.acreate(city="Test City", city_id="12345")
        city_id = await helpers_mixin.get_city_id("Test City", request_)
        assert isinstance(city_id, str)
        assert city_id == "12345"

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestGetCityIdNegative:
    """Класс описывает негативные тестовые случаи для метода get_city_id.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при вызове
    метода get_city_id из класса VacancyHelpersMixin:
    проверка возвращаемого значения при передаче несуществующего города,
    проверка сообщения об ошибке при передаче несуществующего города,
    проверка возвращаемого значения при возникновении ошибки базы данных.
    """

    async def test_get_city_id_nonexistent_city(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тест проверяет возвращаемое значение при передаче несуществующего города.

        Вызывается метод get_city_id с передачей несуществующего города.
        Ожидается, что возвращаемое значение будет равно None.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
        """
        request_.GET = QueryDict("", mutable=True)
        # Проверяем, что функция возвращает None для несуществующего города
        city_id = await helpers_mixin.get_city_id("Nonexistent City", request_)
        assert city_id is None

    async def test_get_city_id_error_message(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
    ) -> None:
        """Тест проверяет сообщение об ошибке при передаче несуществующего города.

        Вызывается метод get_city_id с передачей несуществующего города.
        Ожидается, что сообщение об ошибке будет соответствовать ожидаемому.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
        """
        request_.GET = QueryDict("", mutable=True)
        await helpers_mixin.get_city_id("Nonexistent City", request_)
        # Получаем сообщения Django
        messages = list(get_messages(request_))
        expected_message = "Город с таким названием отсутствует в базе"
        assert isinstance(messages, list)
        assert str(messages[0]) == expected_message

    async def test_get_city_id_database_error(
        self,
        helpers_mixin: VacancyHelpersMixin,
        request_: HttpRequest,
        mocker: MockerFixture,
    ) -> None:
        """Тест проверяет возвращаемое значение при возникновении ошибки базы данных.

        Используется mocker для имитации ошибки базы данных при вызове метода filter
        у модели City.
        Вызывается метод get_city_id с передачей тестового города.
        Ожидается, что возвращаемое значение будет равно None.

        Args:
            helpers_mixin (VacancyHelpersMixin): Миксин с вспомогательными методами.
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            mocker (MockerFixture): Фикстура для создания мок-объектов.
        """
        mocker.patch(
            "parser.models.City.objects.filter", side_effect=Exception("Database error")
        )
        city_id = await helpers_mixin.get_city_id("Test City", request_)
        assert city_id is None
        city_id = await helpers_mixin.get_city_id("Test City", request_)
        assert city_id is None
