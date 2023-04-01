import datetime
from parser.mixins import VacancyScraperMixin
from parser.models import VacancyScraper
from parser.tests.TestAssertions import Assertions

import pytest
from django.db.models import QuerySet
from django.http import HttpRequest


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperMixin:
    """Класс описывает тестовые случаи для миксина VacancyScraperMixin."""

    @pytest.mark.asyncio
    async def test_get_vacancies_from_scraper(
        self,
        request_: HttpRequest,
        scraper_mixin: VacancyScraperMixin,
    ) -> None:
        """Тестирует метод получения вакансий из скрапера.

        Args:
            request_ (HttpRequest): Запрос.
            scraper_mixin (VacancyScraperMixin): Экземпляр VacancyScraperMixin
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
        # Проверяем тип возврщаемого результата
        Assertions.assert_type(result, QuerySet)
        # Проверяем, что результат содержит только 1 значение т.к title_search = True
        Assertions.assert_compare_values(len(result), 1)
        # Проверяем, что результат содержит ожидаемые значения
        Assertions.assert_compare_values(result[0]["title"], "python")

        # Изменяем значение title_search на False
        form_params["title_search"] = False

        result = await scraper_mixin.get_vacancies_from_scraper(request_, form_params)
        # Проверяем, что результат содержит 2 значения т.к title_search = False
        Assertions.assert_compare_values(len(result), 2)

        # Проверяем, что результат содержит ожидаемые значения
        Assertions.assert_compare_values(result[0]["title"], "python")
        Assertions.assert_compare_values(result[1]["description"], "python")

    @pytest.mark.asyncio
    async def test_add_vacancy_to_job_list_from_api(
        self, scraper_mixin: VacancyScraperMixin
    ) -> None:
        """Тестирует метод объединения списка вакансий из API
        со списком вакансий из скрапера в один общий список.

        Args:
            scraper_mixin (VacancyScraperMixin): Экземпляр VacancyScraperMixin.
        """
        # Создаем тестовые данные
        job_list_from_api = [{"title": "Python", "company": "test_company1"}]
        job_list_from_scraper = [{"title": "Java", "company": "test_company2"}]

        # Получаем результат
        result = await scraper_mixin.add_vacancy_to_job_list_from_api(
            job_list_from_api, job_list_from_scraper
        )

        Assertions.assert_type(result, list)
        Assertions.assert_compare_values(len(result), 2)
        Assertions.assert_compare_values(result[0], job_list_from_api[0])
        Assertions.assert_compare_values(result[1], job_list_from_scraper[0])
        Assertions.assert_compare_values(result[1], job_list_from_scraper[0])
