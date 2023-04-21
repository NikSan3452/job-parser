import pytest
from django.contrib.auth.models import User
from django.db.utils import DataError
from profiles.models import Profile


@pytest.mark.django_db(transaction=True)
class TestProfileModelPositive:
    """Класс описывает позитивные тестовые случаи для модели ProfileModel.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при создании
    объектов модели ProfileModel:
    возможность создания объекта модели, проверка возможности оставить поле пустым, 
    проверка значений по умолчанию, проверка метода str, проверка поведения
    полей при удалении связанного объекта, проверка возможности создания объектов
    без указания значения поля
    """

    def test_profile_creation(self, fix_user: User) -> None:
        """Тест проверяет создание объекта модели Profile.

        Создается объект модели Profile с указанными значениями полей.
        Ожидается, что значения полей будут соответствовать указанным при
        создании объекта.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.

        """
        profile = Profile.objects.create(
            user=fix_user, city="Test City", job="Test Job", subscribe=True
        )
        assert profile.user == fix_user
        assert profile.city == "Test City"
        assert profile.job == "Test Job"
        assert profile.subscribe is True

    def test_profile_city_blank(self, fix_user: User) -> None:
        """Тест проверяет возможность оставить поле city модели Profile пустым.

        Создается тестовый пользователь и объект модели Profile с пустым значением
        поля city.
        Ожидается, что значение поля city будет равно пустой строке.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        profile = Profile.objects.create(user=fix_user, city="")
        assert profile.city == ""

    def test_profile_job_blank(self, fix_user: User) -> None:
        """Тест проверяет возможность оставить поле job модели Profile пустым.

        Создается тестовый пользователь и объект модели Profile с пустым значением
        поля job.
        Ожидается, что значение поля job будет равно пустой строке.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        profile = Profile.objects.create(user=fix_user, job="")
        assert profile.job == ""

    def test_profile_user_null(self, fix_user: User) -> None:
        """Тест проверяет возможность создания объекта модели Profile без указания
        значения поля user.

        Создается объект модели Profile без указания значения поля user.
        Ожидается, что значение поля user будет равно None.
        """
        profile = Profile.objects.create()
        assert profile.user is None

    def test_profile_subscribe_default(self, fix_user: User) -> None:
        """Тест проверяет значение по умолчанию для поля subscribe модели Profile.

        Создается тестовый пользователь и объект модели Profile без указания значения
        поля subscribe.
        Ожидается, что значение поля subscribe будет равно False.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        profile = Profile.objects.create(user=fix_user)

        assert profile.subscribe is False

    def test_profile_user_on_delete(self, fix_user: User) -> None:
        """Тест проверяет поведение поля user модели Profile при удалении связанного
        объекта User.

        Создается объект модели Profile с указанным пользователем.
        Удаляется связанный объект User.
        Ожидается, что объект модели Profile также будет удален.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        profile = Profile.objects.create(user=fix_user)
        fix_user.delete()
        with pytest.raises(Profile.DoesNotExist):
            profile.refresh_from_db()

    def test_profile_str(self, fix_user: User) -> None:
        """Тест проверяет метод __str__ модели Profile.

        Создается объект модели Profile с указанным пользователем.
        Ожидается, что строковое представление объекта будет равно имени пользователя.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.

        """
        profile = Profile.objects.create(user=fix_user)
        assert str(profile) == "testuser"


@pytest.mark.django_db(transaction=True)
class TestProfileModelNegative:
    """Класс описывает негативные тестовые случаи для модели ProfileModel.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели ProfileModel:
    проверка ограничений на максимальную длину поля
    """

    def test_profile_city_max_length_exception(self, fix_user: User) -> None:
        """Тест проверяет ограничение на максимальную длину поля city модели Profile.

        Создается тестовый пользователь и объект модели Profile с длиной поля city
        больше максимально допустимой.
        Ожидается возникновение исключения ValidationError при вызове метода full_clean.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        with pytest.raises(DataError):
            profile = Profile.objects.create(user=fix_user, city="x" * 256)
            profile.full_clean()

    def test_profile_job_max_length_exception(self, fix_user: User) -> None:
        """Тест проверяет ограничение на максимальную длину поля job модели Profile.

        Создается тестовый пользователь и объект модели Profile с длиной поля job
        больше максимально допустимой.
        Ожидается возникновение исключения ValidationError при вызове метода full_clean.

        Args:
            fix_user (User): Фикстура возвращающая экземпляр тестового пользователя.
        """
        with pytest.raises(DataError):
            profile = Profile.objects.create(user=fix_user, job="x" * 256)
            profile.full_clean()
