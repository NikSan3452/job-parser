from parser.models import HiddenCompanies

import pytest
from django.contrib.auth.models import User
from django.forms import ValidationError

TEST_COMPANY_NAME = "Test company"


@pytest.mark.django_db(transaction=True)
class TestHiddenCompaniesModelPositive:
    """Класс описывает позитивные тестовые случаи для модели HiddenCompanies.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели HiddenCompanies: возможность создания объекта модели,
    проверка значений по умолчанию, проверка метода str, проверка метаданных модели,
    проверка максимальной длины полей.
    """

    def test_hidden_companies_model_creation(self) -> None:
        """Тест проверяет создание объекта модели HiddenCompanies.

        Создается объект модели User и объект модели HiddenCompanies с указанными
        значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при создании
        объекта.
        """
        user = User.objects.create(username="testuser")
        hidden_company = HiddenCompanies.objects.create(
            user=user, name=TEST_COMPANY_NAME
        )
        assert hidden_company.user == user
        assert hidden_company.name == TEST_COMPANY_NAME
        assert str(hidden_company) == TEST_COMPANY_NAME

    def test_hidden_companies_model_meta(self) -> None:
        """Тест проверяет метаданные модели HiddenCompanies.

        Ожидается, что значения verbose_name и verbose_name_plural будут
        соответствовать указанным в метаданных модели.
        """
        assert HiddenCompanies._meta.verbose_name == "Скрытая компания"
        assert HiddenCompanies._meta.verbose_name_plural == "Скрытые компании"

    def test_name_max_length(self) -> None:
        """Тест проверяет максимальную длину поля name модели HiddenCompanies.

        Ожидается, что максимальная длина поля name будет равна 255 символам.
        """
        max_length = HiddenCompanies._meta.get_field("name").max_length
        assert max_length == 255

    def test_user_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля user модели HiddenCompanies.

        Ожидается, что verbose_name поля user будет равен "Пользователь".
        """
        verbose_name = HiddenCompanies._meta.get_field("user").verbose_name
        assert verbose_name == "Пользователь"

    def test_name_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля name модели HiddenCompanies.

        Ожидается, что verbose_name поля name будет равен "Компания".
        """
        verbose_name = HiddenCompanies._meta.get_field("name").verbose_name
        assert verbose_name == "Компания"


@pytest.mark.django_db(transaction=True)
class TestHiddenCompaniesModelNegative:
    """Класс описывает негативные тестовые случаи для модели HiddenCompanies.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели HiddenCompanies: невозможность создания объекта модели без
    указания обязательных полей, проверка максимальной длины поля name,
    проверка каскадного удаления связанных объектов модели HiddenCompanies при удалении
    объекта модели User, невозможность создания объекта модели с отсутствующим или
    пустым значением поля name.
    """

    def test_create_hidden_companies_without_user(self) -> None:
        """Тест проверяет попытку создания объекта модели HiddenCompanies без указания
        поля user.

        Ожидается, что при попытке создать объект без указания поля user будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            hidden_company = HiddenCompanies(name=TEST_COMPANY_NAME)
            hidden_company.full_clean()

    def test_create_hidden_companies_with_too_long_name(self) -> None:
        """Тест проверяет попытку создания объекта модели HiddenCompanies с слишком
        длинным значением поля name.

        Создается объект модели User и объект модели HiddenCompanies с длиной значения
        поля name больше максимально допустимой.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            hidden_company = HiddenCompanies(user=user, name="a" * 256)
            hidden_company.full_clean()

    def test_cascade_delete_on_user_delete(self):
        """Тест проверяет каскадное удаление связанных объектов модели HiddenCompanies
        при удалении объекта модели User.

        Создается объект модели User и связанный с ним объект модели HiddenCompanies.
        Ожидается, что при удалении объекта модели User связанный с ним объект модели
        HiddenCompanies также будет удален.
        """
        user = User.objects.create(username="testuser")
        HiddenCompanies.objects.create(user=user, name=TEST_COMPANY_NAME)
        assert HiddenCompanies.objects.count() == 1
        user.delete()
        assert HiddenCompanies.objects.count() == 0

    def test_create_hidden_companies_without_name(self) -> None:
        """Тест проверяет попытку создания объекта модели HiddenCompanies без указания
        поля name.

        Создается объект модели User и объект модели HiddenCompanies без указания
        поля name.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            hidden_company = HiddenCompanies(user=user)
            hidden_company.full_clean()

    def test_create_hidden_companies_with_empty_name(self) -> None:
        """Тест проверяет попытку создания объекта модели HiddenCompanies с пустым
        значением поля name.

        Создается объект модели User и объект модели HiddenCompanies с пустым значением
        поля name.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            hidden_company = HiddenCompanies(user=user, name="")
            hidden_company.full_clean()
