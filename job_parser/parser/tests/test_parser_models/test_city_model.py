from parser.models import City
from parser.tests.TestAssertions import Assertions

import pytest


@pytest.mark.django_db(transaction=True)
class TestCityModel:
    """Тестовый случай для модели City приложения parser."""

    def test_city_model(self) -> None:
        """Тестирует модель City."""
        # Создаем тестовый объект
        data = dict(city_id="10000", city="test_city")
        City.objects.create(**data)
        db_obj = City.objects.get(city_id="10000")

        # Проверяем значения текстовых меток (verbose_name)
        Assertions.assert_labels(db_obj, "city", "Город")
        Assertions.assert_labels(db_obj, "city_id", "city id")

        # Проверяем максимальную длину поля
        Assertions.assert_length(db_obj, "city", 255)
        Assertions.assert_length(db_obj, "city_id", 255)

        # Проверяем поле на ограничение уникальности
        Assertions.assert_unique(City, "city", "test_city")
        Assertions.assert_unique(City, "city_id", "10000")
