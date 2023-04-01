import pytest
from parser.models import VacancyScraper

from parser.tests.TestAssertions import Assertions


@pytest.mark.django_db
class TestVacancyScraperModel:
    """Тестовый случай для модели VacancyScraper приложения parser."""

    def setup_data(self) -> VacancyScraper:
        """Устанавливает тестовые данные для модели VacancyScraper.

        Returns:
            VacancyScraper: Объект модели.
        """
        data = dict(
            job_board="test_job_board",
            url="http://test_url.com",
            title="test_title",
            description="test_description",
            city="test_city",
            salary="test_salary",
            company="test_company",
            experience="без опыта",
            type_of_work="удаленная работа",
            remote=False,
            published_at="2023-01-01",
        )

        VacancyScraper.objects.create(**data)
        db_obj = VacancyScraper.objects.get(url=data.get("url", ""))

        return db_obj

    def test_vacancy_scraper_labels(self) -> None:
        """Тестирует текстовые метки модели VacancyScraper."""
        db_obj = self.setup_data()

        fields = {
            "job_board": "Площадка",
            "url": "url",
            "title": "Вакансия",
            "description": "Описание вакансии",
            "city": "Город",
            "salary": "Зарплата",
            "company": "Компания",
            "experience": "Опыт работы",
            "type_of_work": "Тип занятости",
            "remote": "Удаленная работа",
            "published_at": "Дата публикации",
        }

        for key, value in fields.items():
            Assertions.assert_labels(db_obj, key, value)

    def test_vacancy_scraper_lenght(self) -> None:
        """Тестирует максимальную длину полей."""
        lenghts = {
            "job_board": 255,
            "title": 255,
            "city": 255,
            "salary": 255,
            "company": 255,
            "experience": 100,
            "type_of_work": 255,
        }
        for key, value in lenghts.items():
            Assertions.assert_length(VacancyScraper, key, value)
