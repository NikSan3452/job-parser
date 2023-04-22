from parser.models import FavouriteVacancy

import pytest
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

TEST_URL = "https://example.com/vacancy/1"
TEST_TITLE = "Test title"


@pytest.mark.django_db(transaction=True)
class TestFavouriteVacancyModelPositive:
    """Класс описывает позитивные тестовые случаи для модели FavouriteVacancy.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели FavouriteVacancy: возможность создания объекта модели,
    проверка значений по умолчанию, проверка метода str, проверка метаданных модели,
    проверка максимальной длины и уникальности полей.
    """

    def test_favourite_vacancy_model_creation(self) -> None:
        """Тест проверяет создание объекта модели FavouriteVacancy.

        Создается объект модели User и объект модели FavouriteVacancy с указанными
        значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при создании
        объекта.
        """
        user = User.objects.create(username="testuser")
        favourite_vacancy = FavouriteVacancy.objects.create(
            user=user, url=TEST_URL, title=TEST_TITLE
        )
        assert favourite_vacancy.user == user
        assert favourite_vacancy.url == TEST_URL
        assert favourite_vacancy.title == TEST_TITLE
        assert str(favourite_vacancy) == TEST_TITLE

    def test_favourite_vacancy_model_meta(self) -> None:
        """Тест проверяет метаданные модели FavouriteVacancy.

        Ожидается, что значения verbose_name и verbose_name_plural будут
        соответствовать указанным в метаданных модели.
        """
        assert FavouriteVacancy._meta.verbose_name == "Избранная вакансия"
        assert FavouriteVacancy._meta.verbose_name_plural == "Избранные вакансии"

    def test_title_max_length(self) -> None:
        """Тест проверяет максимальную длину поля title модели FavouriteVacancy.

        Ожидается, что максимальная длина поля title будет равна 250 символам.
        """
        max_length = FavouriteVacancy._meta.get_field("title").max_length
        assert max_length == 250

    def test_url_unique(self) -> None:
        """Тест проверяет уникальность поля url модели FavouriteVacancy.

        Ожидается, что поле url будет уникальным.
        """
        unique = FavouriteVacancy._meta.get_field("url").unique
        assert unique is True

    def test_title_blank(self) -> None:
        """Тест проверяет возможность оставить поле title пустым.

        Ожидается, что поле title не может быть пустым.
        """
        blank = FavouriteVacancy._meta.get_field("title").blank
        assert blank is False

    def test_url_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля url.

        Ожидается, что значение по умолчанию для поля url будет равно False.
        """
        null = FavouriteVacancy._meta.get_field("url").null
        assert null is False

    def test_title_null(self) -> None:
        """Тест проверяет значение по умолчанию для поля title.

        Ожидается, что значение по умолчанию для поля title будет равно False.
        """
        null = FavouriteVacancy._meta.get_field("title").null
        assert null is False

    def test_url_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля url модели FavouriteVacancy.

        Ожидается, что verbose_name поля url будет равен "url".
        """
        verbose_name = FavouriteVacancy._meta.get_field("url").verbose_name
        assert verbose_name == "url"

    def test_title_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля title модели FavouriteVacancy.

        Ожидается, что verbose_name поля title будет равен "Вакансия".
        """
        verbose_name = FavouriteVacancy._meta.get_field("title").verbose_name
        assert verbose_name == "Вакансия"

    def test_user_verbose_name(self) -> None:
        """Тест проверяет verbose_name поля user модели FavouriteVacancy.

        Ожидается, что verbose_name поля user будет равен "Пользователь".
        """
        verbose_name = FavouriteVacancy._meta.get_field("user").verbose_name
        assert verbose_name == "Пользователь"


@pytest.mark.django_db(transaction=True)
class TestFavouriteVacancyModelNegative:
    """Класс описывает негативные тестовые случаи для модели FavouriteVacancy.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели FavouriteVacancy: невозможность создания объекта модели без
    указания обязательных полей, проверка уникальности поля url, проверка максимальной
    длины поля title, проверка каскадного удаления связанных объектов модели
    FavouriteVacancy при удалении объекта модели User.
    """

    def test_create_favourite_vacancy_without_user(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy без
        указания поля user.

        Ожидается, что при попытке создать объект без указания поля user будет вызвано
        исключение ValidationError.
        """
        with pytest.raises(ValidationError):
            favourite_vacancy = FavouriteVacancy(url=TEST_URL, title=TEST_TITLE)
            favourite_vacancy.full_clean()

    def test_create_favourite_vacancy_without_url(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy без указания
            поля url.

        Создается объект модели User и объект модели FavouriteVacancy без указания
        поля url.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            favourite_vacancy = FavouriteVacancy(user=user, title=TEST_TITLE)
            favourite_vacancy.full_clean()

    def test_create_favourite_vacancy_without_title(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy без указания
        поля title.

        Создается объект модели User и объект модели FavouriteVacancy без указания
        поля title.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            favourite_vacancy = FavouriteVacancy(user=user, url=TEST_URL)
            favourite_vacancy.full_clean()

    def test_create_favourite_vacancy_with_duplicate_url(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy с
        дублирующимся значением поля url.

        Создается объект модели User и два объекта модели FavouriteVacancy с одинаковым
        значением поля url.
        Ожидается, что при попытке создать второй объект будет вызвано исключение
        ValidationError.
        """
        user = User.objects.create(username="testuser")
        FavouriteVacancy.objects.create(user=user, url=TEST_URL, title=TEST_TITLE)
        with pytest.raises(ValidationError):
            favourite_vacancy = FavouriteVacancy(
                user=user,
                url=TEST_URL,
                title="Другая тестовая вакансия",
            )
            favourite_vacancy.full_clean()

    def test_create_favourite_vacancy_with_too_long_title(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy с слишком
        длинным значением поля title.

        Создается объект модели User и объект модели FavouriteVacancy с длиной значения
        поля title больше максимально допустимой.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            favourite_vacancy = FavouriteVacancy(
                user=user, url=TEST_URL, title="a" * 251
            )
            favourite_vacancy.full_clean()

    def test_create_favourite_vacancy_with_empty_title(self) -> None:
        """Тест проверяет попытку создания объекта модели FavouriteVacancy с пустым
        значением поля title.

        Создается объект модели User и объект модели FavouriteVacancy с пустым
        значением поля title.
        Ожидается, что при попытке создать объект будет вызвано исключение
        ValidationError.
        """
        with pytest.raises(ValidationError):
            user = User.objects.create(username="testuser")
            favourite_vacancy = FavouriteVacancy(user=user, url=TEST_URL, title="")
            favourite_vacancy.full_clean()

    def test_cascade_delete_on_user_delete(self):
        """Тест проверяет каскадное удаление связанных объектов модели FavouriteVacancy
        при удалении объекта модели User.

        Создается объект модели User и связанный с ним объект модели FavouriteVacancy.
        Ожидается, что при удалении объекта модели User связанный с ним объект модели
        FavouriteVacancy также будет удален.
        """
        user = User.objects.create(username="testuser")
        FavouriteVacancy.objects.create(user=user, url=TEST_URL, title=TEST_TITLE)
        assert FavouriteVacancy.objects.count() == 1
        user.delete()
        assert FavouriteVacancy.objects.count() == 0
