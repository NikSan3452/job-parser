import datetime
from parser.mixins import VacancyScraperMixin
from parser.models import VacancyScraper

import pytest
from django.db.models import QuerySet
from django.http import HttpRequest
from pytest_mock import MockerFixture


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperMixinPositive:
    """Класс описывает позитивные тестовые случаи для класса VacancyScraperMixin.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при работе с
    классом VacancyScraperMixin: проверка получения вакансий из скрапера и добавление
    вакансий в список вакансий из API.
    """

    @pytest.mark.asyncio
    async def test_get_vacancies_from_scraper(
        self,
        request_: HttpRequest,
        scraper_mixin: VacancyScraperMixin,
    ) -> None:
        """Тест проверяет получение вакансий из скрапера.

        Создаются два объекта модели VacancyScraper с указанными значениями полей.
        Вызывается метод get_vacancies_from_scraper с параметрами формы, в которых
        активен флажок для поиска в заголовках вакансий.
        Ожидается, что метод вернет QuerySet с одним объектом, соответствующим
        указанным параметрам поиска.
        Затем вызывается метод get_vacancies_from_scraper с измененными параметрами
        формы, чтобы искать значение поля title одновременно и в описании и в
        заголовках вакансий.
        Ожидается, что метод вернет QuerySet с двумя объектами, соответствующими
        указанным параметрам поиска.

        Args:
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            scraper_mixin (VacancyScraperMixin): Экземпляр класса VacancyScraperMixin.
        """
        # Создаем записи в базе данных для тестирования
        await VacancyScraper.objects.acreate(
            job_board="Habr career",
            title="python",
            url="http://example.com/vacancy1",
            description="описание",
            published_at=datetime.date.today(),
        )
        await VacancyScraper.objects.acreate(
            job_board="Habr career",
            title="java",
            url="http://example.com/vacancy2",
            description="python",
            published_at=datetime.date.today(),
        )

        # Создаем словарь параметров формы
        form_params = {
            "job_board": "Habr career",
            "job": "Python",
            "title_search": True,
        }

        # Вызываем функцию get_vacancies_from_scraper с фиктивным запросом и параметрами формы
        result = await scraper_mixin.get_vacancies_from_scraper(request_, form_params)
        # Проверяем тип возвращаемого результата
        assert isinstance(result, QuerySet)
        # Проверяем, что результат содержит только 1 значение т.к title_search = True
        assert len(result) == 1
        # Проверяем, что результат содержит ожидаемые значения
        assert result[0]["title"] == "python"

        # Изменяем значение title_search на False
        form_params["title_search"] = False

        result = await scraper_mixin.get_vacancies_from_scraper(request_, form_params)
        # Проверяем, что результат содержит 2 значения т.к title_search = False
        assert len(result) == 2

        # Проверяем, что результат содержит ожидаемые значения
        assert result[0]["title"] == "python"
        assert result[1]["description"] == "python"

    @pytest.mark.asyncio
    async def test_add_vacancy_to_job_list_from_api(
        self, scraper_mixin: VacancyScraperMixin
    ) -> None:
        """Тест проверяет добавление вакансий в список вакансий из API.

        Создаются два списка вакансий: один из API и один из скрапера.
        Вызывается метод add_vacancy_to_job_list_from_api с этими списками в качестве
        аргументов.
        Ожидается, что метод вернет список, содержащий элементы обоих списков.

        Args:
            scraper_mixin (VacancyScraperMixin): Экземпляр класса VacancyScraperMixin.
        """
        # Создаем тестовые данные
        job_list_from_api = [{"title": "Python", "company": "test_company1"}]
        job_list_from_scraper = [{"title": "Java", "company": "test_company2"}]

        # Получаем результат
        result = await scraper_mixin.add_vacancy_to_job_list_from_api(
            job_list_from_api, job_list_from_scraper
        )

        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == job_list_from_api[0]
        assert result[1] == job_list_from_scraper[0]


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperMixinNegative:
    """Класс описывает негативные тестовые случаи для класса VacancyScraperMixin.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при работе с
    классом VacancyScraperMixin: проверка обработки исключений при получении вакансий
    из скрапера и добавление пустых списков вакансий из API и скрапера.
    """

    @pytest.mark.asyncio
    async def test_get_vacancies_from_scraper_exceptions(
        self,
        request_: HttpRequest,
        scraper_mixin: VacancyScraperMixin,
        mocker: MockerFixture,
    ) -> None:
        """Тест проверяет обработку исключений при получении вакансий из скрапера.

        Создается форма с параметрами для поиска вакансий.
        Вызывается метод get_vacancies_from_scraper с этой формой в качестве аргумента.
        Ожидается, что метод вызовет исключение.
        Затем вызывается метод get_vacancies_from_scraper с измененными параметрами
        формы, чтобы искать значения поля job как в описании, так и в заголовка
        вакансии.
        Ожидается, что метод вызовет исключение.

        Args:
            request_ (HttpRequest): Фикстура для создания фиктивных запросов.
            scraper_mixin (VacancyScraperMixin): Экземпляр класса VacancyScraperMixin.
            mocker (MockerFixture): Фикстура для создания мок-объектов.
        """
        form_params = {
            "job_board": "Habr career",
            "job": "Python",
            "title_search": True,
        }

        with pytest.raises(Exception):
            with mocker.patch(
                "VacancyScraper.objects.filter",
                side_effect=Exception("Test exception"),
            ):
                await scraper_mixin.get_vacancies_from_scraper(request_, form_params)

        form_params["title_search"] = False

        with pytest.raises(Exception):
            with mocker.patch(
                "VacancyScraper.objects.filter",
                side_effect=Exception("Test exception"),
            ):
                await scraper_mixin.get_vacancies_from_scraper(request_, form_params)

    @pytest.mark.asyncio
    async def test_add_vacancy_to_job_list_from_api_empty(
        self, scraper_mixin: VacancyScraperMixin
    ) -> None:
        """Тест проверяет добавление пустых списков вакансий из API и скрапера.

        Создаются два пустых списка вакансий: один из API и один из скрапера.
        Вызывается метод add_vacancy_to_job_list_from_api с этими списками в качестве 
        аргументов.
        Ожидается, что метод вернет пустой список.

        Args:
            scraper_mixin (VacancyScraperMixin): Экземпляр класса VacancyScraperMixin.
        """
        job_list_from_api = []
        job_list_from_scraper = []

        result = await scraper_mixin.add_vacancy_to_job_list_from_api(
            job_list_from_api, job_list_from_scraper
        )

        assert isinstance(result, list)
        assert len(result) == 0
