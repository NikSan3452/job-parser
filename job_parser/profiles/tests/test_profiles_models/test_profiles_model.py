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
    проверка значений по умолчанию, проверка возможности создания объектов
    без указания значения поля, проверка максимальное длины поля
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

    def test_user_null(self):
        """Тест проверяет значение null для поля user модели Profile.

        Ожидается, что значение null для поля user будет равно True.
        """
        null = Profile._meta.get_field("user").null
        assert null is True

    def test_city_max_length(self):
        """Тест проверяет максимальную длину поля city модели Profile.

        Ожидается, что максимальная длина поля city будет равна 255 символам.
        """
        max_length = Profile._meta.get_field("city").max_length
        assert max_length == 255

    def test_city_null(self):
        """Тест проверяет значение null для поля city модели Profile.

        Ожидается, что значение null для поля city будет равно True.
        """
        null = Profile._meta.get_field("city").null
        assert null is True

    def test_city_blank(self):
        """Тест проверяет значение blank для поля city модели Profile.

        Ожидается, что значение blank для поля city будет равно True.
        """
        blank = Profile._meta.get_field("city").blank
        assert blank is True

    def test_job_max_length(self):
        """Тест проверяет максимальную длину поля job модели Profile.

        ожидается, что максимальная длина поля job будет равна 255 символам.
        """
        max_length = Profile._meta.get_field("job").max_length
        assert max_length == 255

    def test_job_null(self):
        """Тест проверяет значение null для поля job модели Profile.

        ожидается, что значение null для поля job будет равно True.
        """
        null = Profile._meta.get_field("job").null
        assert null is True

    def test_job_blank(self):
        """Тест проверяет значение blank для поля job модели Profile.

        ожидается, что значение blank для поля job будет равно True.
        """
        blank = Profile._meta.get_field("job").blank
        assert blank is True

    def test_subscribe_default(self):
        """Тест проверяет значение по умолчанию для поля subscribe модели Profile.

        ожидается, что значение по умолчанию для поля subscribe будет равно False.
        """
        default = Profile._meta.get_field("subscribe").default
        assert default is False


@pytest.mark.django_db(transaction=True)
class TestProfileModelNegative:
    """Класс описывает негативные тестовые случаи для модели ProfileModel.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при создании
    объектов модели ProfileModel:
    проверка ограничений на максимальную длину поля, проверка поведения полей при
    удалении связанного объекта.
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
