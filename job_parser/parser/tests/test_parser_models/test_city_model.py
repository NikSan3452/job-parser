from parser.models import City

import pytest
from django.core.exceptions import ValidationError


@pytest.mark.django_db(transaction=True)
class TestCityModelPositive:
    """Класс описывает позитивные тестовые случаи для модели City.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели City:
    возможность создания объекта модели, проверка максимальной длины полей,
    проверка уникальности полей, проверка возможности оставить поле пустым,
    проверка значений по умолчанию для полей.
    """

    def test_city_model_creation(self) -> None:
        """Тест проверяет создание объекта модели City.

        Создается объект модели City с указанными значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при
        создании объекта.
        """
        city = City.objects.create(city_id="1", city="Москва")
        assert city.city_id == "1"
        assert city.city == "Москва"
        assert str(city) == "Москва"

    def test_city_model_meta(self) -> None:
        """Тест проверяет метаданные модели City.

        Ожидается, что значения verbose_name и verbose_name_plural будут соответствовать
        указанным в метаданных модели.
        """
        assert City._meta.verbose_name == "Город"
        assert City._meta.verbose_name_plural == "Города"

    def test_city_id_max_length(self) -> None:
        """Тест проверяет максимальную длину поля city_id модели City.

        Ожидается, что максимальная длина поля city_id будет равна 255 символам.
        """
        max_length = City._meta.get_field("city_id").max_length
        assert max_length == 255

    def test_city_max_length(self) -> None:
        """Тест проверяет максимальную длину поля city модели City.

        Ожидается, что максимальная длина поля city будет равна 255 символам.
        """
        max_length = City._meta.get_field("city").max_length
        assert max_length == 255

    def test_city_id_unique(self) -> None:
        """Тест проверяет уникальность поля city_id модели City.

        Ожидается, что поле city_id будет уникальным.
        """
        unique = City._meta.get_field("city_id").unique
        assert unique is True

    def test_city_unique(self) -> None:
        """Тест проверяет уникальность поля city модели City.

        Ожидается, что поле city будет уникальным.
        """
        unique = City._meta.get_field("city").unique
        assert unique is True

    def test_city_id_blank(self) -> None:
        """Тест проверяет возможность оставить поле city_id пустым.

        Ожидается, что поле city_id не может быть пустым.
        """
        blank = City._meta.get_field("city_id").blank
        assert blank is False

    def test_city_blank(self) -> None:
        """Тест проверяет возможность оставить поле city пустым.

        Ожидается, что поле city не может быть пустым.
        """
        blank = City._meta.get_field("city").blank
        assert blank is False

    def test_city_id_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля city_id.

        Ожидается, что значение по умолчанию для поля city_id будет равно False.
        """
        null = City._meta.get_field("city_id").null
        assert null is False

    def test_city_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля city.

        Ожидается, что значение по умолчанию для поля city будет равно False.
        """
        null = City._meta.get_field("city").null
        assert null is False


@pytest.mark.django_db(transaction=True)
class TestCityModelNegative:
    """Класс описывает негативные тестовые случаи для модели City.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели City:
    попытка создания объекта без указания обязательных полей, попытка создания объекта
    с дублирующимися значениями уникальных полей, попытка создания объекта с слишком
    длинными значениями полей, попытка создания объекта с пустыми значениями полей.
    """

    def test_create_city_without_city_id(self) -> None:
        """Тест проверяет попытку создания объекта модели City без указания city_id.

        Ожидается, что при попытке создать объект без указания city_id будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city="Москва")
            city.full_clean()

    def test_create_city_without_city(self) -> None:
        """Тест проверяет попытку создания объекта модели City без указания city.

        Ожидается, что при попытке создать объект без указания city будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city_id="1")
            city.full_clean()

    def test_create_city_with_duplicate_city_id(self) -> None:
        """Тест проверяет попытку создания объекта модели City с дублирующимся
        значением city_id.

        Создается объект модели City с указанным значением city_id.
        Ожидается, что при попытке создать еще один объект с таким же значением city_id
        будет вызвано исключение ValidationError.
        """
        City.objects.create(city_id="1", city="Москва")
        with pytest.raises(ValidationError):
            city = City(city_id="1", city="Санкт-Петербург")
            city.full_clean()

    def test_create_city_with_duplicate_city(self) -> None:
        """Тест проверяет попытку создания объекта модели City с дублирующимся
        значением city.

        Создается объект модели City с указанным значением city.
        Ожидается, что при попытке создать еще один объект с таким же значением city
        будет вызвано исключение ValidationError.
        """
        City.objects.create(city_id="1", city="Москва")
        with pytest.raises(ValidationError):
            city = City(city_id="2", city="Москва")
            city.full_clean()

    def test_create_city_with_too_long_city_id(self) -> None:
        """Тест проверяет попытку создания объекта модели City со слишком длинным
        значением city_id.

        Ожидается, что при попытке создать объект со значением длиной более 255 символов
        для поля city_id будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city_id="a" * 256, city="Москва")
            city.full_clean()

    def test_create_city_with_too_long_city(self) -> None:
        """Тест проверяет попытку создания объекта модели City со слишком длинным
        значением city.

        Ожидается, что при попытке создать объект со значением длиной более 255 символов
        для поля city будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city_id="1", city="a" * 256)
            city.full_clean()

    def test_create_city_with_empty_city_id(self) -> None:
        """Тест проверяет попытку создания объекта модели City с пустым
        значением city_id.

        Ожидается, что при попытке создать объект с пустым значением для поля city_id
        будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city_id="", city="Москва")
            city.full_clean()

    def test_create_city_with_empty_city(self) -> None:
        """Тест проверяет попытку создания объекта модели City с пустым значением city.

        Ожидается, что при попытке создать объект с пустым значением для поля city
        будет вызвано исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            city = City(city_id="1", city="")
            city.full_clean()
