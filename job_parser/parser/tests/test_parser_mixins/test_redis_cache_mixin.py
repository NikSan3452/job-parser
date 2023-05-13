from parser.mixins import RedisCacheMixin

import pytest
from django.http import HttpRequest
from pytest_mock import MockerFixture

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestRedisCacheMixinPositive:
    """Класс описывает позитивные тестовые случаи для миксина RedisCacheMixin.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных позитивных сценариев при работе
    с миксином RedisCacheMixin: создание ключа кэша, сохранение данных в кэше,
    получение данных из кэша.
    """

    async def test_create_cache_key(
        self, cache_key: RedisCacheMixin, request_: HttpRequest
    ) -> None:
        """Тест проверяет создание ключа кэша.

        Вызывается метод `create_cache_key` с передачей объекта `request_`.
        Ожидается, что возвращаемое значение будет соответствовать ключу сессии
        объекта `request_`.

        Args:
            cache_key (RedisCacheMixin): Фикстура возвращающая ключ кэша.
            request_ (HttpRequest): Фикстура возвращающая объект запроса.
        """
        session_id = f"session_id:{request_.session.session_key}"
        assert cache_key == session_id

    async def test_set_data_to_cache(
        self, redis_mixin: RedisCacheMixin, cache_key: RedisCacheMixin
    ) -> None:
        """Тест проверяет сохранение данных в кэше.

        Вызывается метод `set_data_to_cache` с передачей списка данных.
        Затем вызывается метод `get_data_from_cache` для получения сохраненных данных.
        Ожидается, что возвращаемые данные будут соответствовать сохраненным.

        Args:
            redis_mixin (RedisCacheMixin): Фикстура возвращающая экземпляр миксина.
            cache_key (RedisCacheMixin): Фикстура возвращающая ключ кэша.
        """
        job_list = [{"job": "test1"}, {"job": "test2"}]
        await redis_mixin.set_data_to_cache(job_list)
        result = await redis_mixin.get_data_from_cache()
        assert job_list == result

@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestRedisCacheMixinNegative:
    """Класс описывает негативные тестовые случаи для миксина RedisCacheMixin.

    Декоратор `@pytest.mark.django_db` указывает pytest на необходимость использования
    базы данных.
    Параметр `transaction=True` указывает на использование транзакций для ускорения
    и изоляции тестов.
    Этот класс содержит тесты для проверки различных негативных сценариев при работе
    с миксином RedisCacheMixin: создание ключа кэша с неверными параметрами,
    сохранение пустого списка в кэше, получение данных из кэша с неверным ключом,
    обработка ошибок при работе с модулем pickle и объектом settings.CACHE.
    """

    def raise_exception(self) -> None:
        """Метод вызывает исключение.

        Используется для замены функций, которые должны вызвать исключение в тестах.
        """
        raise Exception("Test exception")

    async def test_create_cache_key_with_invalid_request(
        self, cache_key: RedisCacheMixin
    ) -> None:
        """Тест проверяет создание ключа кэша с неверным параметром запроса.

        Вызывается метод `create_cache_key` с передачей значения `None`.
        Ожидается возникновение исключения `AttributeError`.

        Args:
            cache_key (RedisCacheMixin): Фикстура возвращающая ключ кэша.
        """
        with pytest.raises(AttributeError):
            await cache_key.create_cache_key(None)

    async def test_get_data_from_cache_with_invalid_key(
        self, redis_mixin: RedisCacheMixin
    ) -> None:
        """Тест проверяет получение данных из кэша с неверным ключом.

        Устанавливается значение "invalid_key" для свойства `cache_key`
        объекта `redis_mixin`.
        Вызывается метод `get_data_from_cache`.
        Ожидается, что возвращаемое значение будет равно `None`.

        Args:
            redis_mixin (RedisCacheMixin): Фикстура возвращающая экземпляр миксина.
        """
        redis_mixin.cache_key = "invalid_key"
        result = await redis_mixin.get_data_from_cache()
        assert result is None

    async def test_set_data_to_cache_with_empty_list(
        self, redis_mixin: RedisCacheMixin, cache_key: RedisCacheMixin
    ) -> None:
        """Тест проверяет сохранение пустого списка в кэше.

        Вызывается метод `set_data_to_cache` с передачей пустого списка.
        Затем вызывается метод `get_data_from_cache` для получения сохраненных данных.
        Ожидается, что возвращаемые данные будут соответствовать сохраненным.

        Args:
            redis_mixin (RedisCacheMixin): Фикстура возвращающая экземпляр миксина.
            cache_key (RedisCacheMixin): Фикстура возвращающая ключ кэша.
        """
        job_list: list = []
        await redis_mixin.set_data_to_cache(job_list)
        result = await redis_mixin.get_data_from_cache()
        assert result == job_list

    async def test_get_data_from_cache_with_none_cache(
        self, redis_mixin: RedisCacheMixin, mocker: MockerFixture
    ) -> None:
        """Тест проверяет получение данных из кэша при отсутствии объекта кэша.

        Заменяется объект `settings.CACHE` на значение `None` с помощью фикстуры
        `mocker`.
        Вызывается метод `get_data_from_cache`.
        Ожидается возникновение исключения `AttributeError`.

        Args:
            redis_mixin (RedisCacheMixin): Фикстура возвращающая экземпляр миксина.
            mocker (MockerFixture): Фикстура для замены объектов и функций в тестах.
        """
        mocker.patch("job_parser.settings.CACHE", None)
        with pytest.raises(AttributeError):
            await redis_mixin.get_data_from_cache()

    async def test_set_data_to_cache_with_none_cache(
        self, redis_mixin: RedisCacheMixin, mocker: MockerFixture
    ) -> None:
        """Тест проверяет установку данных в кэш с отсутствующим кэшем.

        Устанавливает значение CACHE в None и создает список работ. Ожидается,
        что при попытке установить данные в кэш будет вызвано исключение AttributeError.

        Args:
            redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.
            mocker (MockerFixture): Фикстура для создания заглушек и моков.
        """
        mocker.patch("job_parser.settings.CACHE", None)
        job_list = [{"job": "test1"}, {"job": "test2"}]
        with pytest.raises(AttributeError):
            await redis_mixin.set_data_to_cache(job_list)

    async def test_get_data_from_cache_with_pickle_error(
        self, redis_mixin: RedisCacheMixin, mocker: MockerFixture
    ) -> None:
        """Тест проверяет получение данных из кэша с ошибкой pickle.

        Создает заглушку для pickle.loads с вызовом исключения. Ожидается,
        что при попытке получить данные из кэша будет вызвано исключение.

        Args:
            redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.
            mocker (MockerFixture): Фикстура для создания заглушек и моков.
        """
        mocker.patch("pickle.loads", side_effect=self.raise_exception)
        with pytest.raises(Exception):
            await redis_mixin.get_data_from_cache()

    async def test_set_data_to_cache_with_pickle_error(
        self, redis_mixin: RedisCacheMixin, mocker: MockerFixture
    ) -> None:
        """Тест проверяет установку данных в кэш с ошибкой pickle.

        Создает заглушку для pickle.dumps с вызовом исключения и создает список работ.
        Ожидается, что при попытке установить данные в кэш будет вызвано исключение.

        Args:
            redis_mixin (RedisCacheMixin): Экземпляр RedisCacheMixin.
            mocker (MockerFixture): Фикстура для создания заглушек и моков.
        """
        mocker.patch("pickle.dumps", side_effect=self.raise_exception)
        job_list = [{"job": "test1"}, {"job": "test2"}]
        with pytest.raises(Exception):
            await redis_mixin.set_data_to_cache(job_list)
