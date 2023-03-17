import pytest

from parser.models import (
    City,
    VacancyScraper,
    FavouriteVacancy,
    VacancyBlackList,
    HiddenCompanies,
)
from parser.tests.Assertions.ModelsAssertions import ModelsAssertions


@pytest.mark.django_db(transaction=True)
class TestCityModel:
    """Тестовый случай для модели City приложения parser."""

    def test_city_model(self):
        """Тестирует модель City."""
        # Создаем тестовый объект
        City.objects.create(city_id="10000", city="test_city")

        # Получаем тестовый объект
        db_city = City.objects.get(city_id="10000")

        # Проверяем значения текстовых меток (verbose_name)
        ModelsAssertions.assert_labels(db_city, "city", "Город")
        ModelsAssertions.assert_labels(db_city, "city_id", "city id")

        # Проверяем максимальную длину поля
        ModelsAssertions.assert_length(db_city, "city", 255)
        ModelsAssertions.assert_length(db_city, "city_id", 255)

        # Проверяем поле на ограничение уникальности
        ModelsAssertions.assert_unique(City, "city", "test_city")
        ModelsAssertions.assert_unique(City, "city_id", "10000")


@pytest.mark.django_db(transaction=True)
class TestVacancyScraperModel:
    """Тестовый случай для модели VacancyScraper приложения parser."""

    pass


@pytest.mark.django_db(transaction=True)
class TestFavouriteVacancyModel:
    pass


@pytest.mark.django_db(transaction=True)
class TestVacancyBlackListModel:
    """Тестовый случай для модели FavouriteVacancy приложения parser."""

    pass


@pytest.mark.django_db(transaction=True)
class TestHiddenCompaniesModel:
    """Тестовый случай для модели HiddenCompanies приложения parser."""

    pass
