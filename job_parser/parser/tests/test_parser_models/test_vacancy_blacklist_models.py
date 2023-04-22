from parser.models import VacancyBlackList

import pytest
from django.contrib.auth.models import User
from django.forms import ValidationError

TEST_URL = "https://example.com/vacancy/1"
TEST_TITLE = "Test title"


@pytest.mark.django_db(transaction=True)
class TestVacancyBlackListModelPositive:
    """Класс описывает позитивные тестовые случаи для модели VacancyBlackList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели VacancyBlackList: возможность создания объекта модели,
    проверка значений по умолчанию, проверка метода str, проверка метаданных модели,
    проверка максимальной длины и уникальности полей.
    """

    def test_vacancy_black_list_model_creation(self) -> None:
        """Тест проверяет создание объекта модели VacancyBlackList.

        Создается объект модели User и объект модели VacancyBlackList с указанными
        значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при создании
        объекта.
        """
        user = User.objects.create(username="testuser")
        vacancy_black_list = VacancyBlackList.objects.create(
            user=user, url=TEST_URL, title=TEST_TITLE
        )
        assert vacancy_black_list.user == user
        assert vacancy_black_list.url == TEST_URL
        assert vacancy_black_list.title == TEST_TITLE
        assert str(vacancy_black_list) == TEST_URL

    def test_vacancy_black_list_model_meta(self) -> None:
        """Тест проверяет метаданные модели VacancyBlackList.

        Ожидается, что значения verbose_name и verbose_name_plural будут
        соответствовать указанным в метаданных модели.
        """
        assert VacancyBlackList._meta.verbose_name == "Вакансия в черном списке"
        assert VacancyBlackList._meta.verbose_name_plural == "Вакансии в черном списке"

    def test_url_unique(self) -> None:
        """Тест проверяет уникальность поля url модели VacancyBlackList.

        Ожидается, что поле url будет уникальным.
        """
        unique = VacancyBlackList._meta.get_field("url").unique
        assert unique is True

    def test_title_max_length(self) -> None:
        """Тест проверяет максимальную длину поля title модели VacancyBlackList.

        Ожидается, что максимальная длина поля title будет равна 250 символам.
        """
        max_length = VacancyBlackList._meta.get_field("title").max_length
        assert max_length == 250

    def test_title_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля title.

        Ожидается, что значение по умолчанию для поля title будет равно True."""

        null = VacancyBlackList._meta.get_field("title").null
        assert null is True

    def test_url_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля url.

        Ожидается, что значение по умолчанию для поля url будет равно False."""

        null = VacancyBlackList._meta.get_field("url").null
        assert null is False

    def test_title_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля title модели VacancyBlackList.

        Ожидается, что verbose_name поля title будет равен "Вакансия".
        """
        verbose_name = VacancyBlackList._meta.get_field("title").verbose_name
        assert verbose_name == "Вакансия"

    def test_user_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля user модели VacancyBlackList.

        Ожидается, что verbose_name поля user будет равен "Пользователь".
        """
        verbose_name = VacancyBlackList._meta.get_field("user").verbose_name
        assert verbose_name == "Пользователь"

@pytest.mark.django_db(transaction=True)
class TestVacancyBlackListModelNegative:
    """Класс описывает негативные тестовые случаи для модели VacancyBlackList.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели VacancyBlackList: невозможность создания объекта модели без
    указания обязательных полей, проверка уникальности поля url, проверка максимальной
    длины поля title, проверка каскадного удаления связанных объектов модели
    VacancyBlackList при удалении объекта модели User.
    """

    def test_create_vacancy_black_list_without_user(self) -> None:
        """Тест проверяет попытку создания объекта модели VacancyBlackList без
        указания поля user.

        Ожидается, что при попытке создать объект без указания поля user будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            vacancy_black_list = VacancyBlackList(url=TEST_URL, title=TEST_TITLE)
            vacancy_black_list.full_clean()

    def test_create_vacancy_black_list_without_url(self) -> None:
        """Тест проверяет попытку создания объекта модели VacancyBlackList без указания
        поля url.

        Создается объект модели User и объект модели VacancyBlackList без указания
        поля url.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            vacancy_black_list = VacancyBlackList(user=user, title=TEST_TITLE)
            vacancy_black_list.full_clean()

    def test_create_vacancy_black_list_with_duplicate_url(self) -> None:
        """Тест проверяет попытку создания объекта модели VacancyBlackList с
        дублирующимся значением поля url.

        Создается объект модели User и два объекта модели VacancyBlackList с одинаковым
        значением поля url.
        Ожидается, что при попытке создать второй объект будет вызвано исключение
        ValidationError.
        """
        user = User.objects.create(username="testuser")
        VacancyBlackList.objects.create(user=user, url=TEST_URL, title=TEST_TITLE)
        with pytest.raises(ValidationError):
            vacancy_black_list = VacancyBlackList(
                user=user,
                url=TEST_URL,
                title="Другая тестовая вакансия",
            )
            vacancy_black_list.full_clean()

    def test_create_vacancy_black_list_with_too_long_title(self) -> None:
        """Тест проверяет попытку создания объекта модели VacancyBlackList с слишком
        длинным значением поля title.

        Создается объект модели User и объект модели VacancyBlackList с длиной значения
        поля title больше максимально допустимой.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            vacancy_black_list = VacancyBlackList(
                user=user, url=TEST_URL, title="a" * 251
            )
            vacancy_black_list.full_clean()

    def test_cascade_delete_on_user_delete(self):
        """Тест проверяет каскадное удаление связанных объектов модели VacancyBlackList
        при удалении объекта модели User.

        Создается объект модели User и связанный с ним объект модели VacancyBlackList.
        Ожидается, что при удалении объекта модели User связанный с ним объект модели
        VacancyBlackList также будет удален.
        """
        user = User.objects.create(username="testuser")
        VacancyBlackList.objects.create(user=user, url=TEST_URL, title=TEST_TITLE)
        assert VacancyBlackList.objects.count() == 1
        user.delete()
        assert VacancyBlackList.objects.count() == 0
