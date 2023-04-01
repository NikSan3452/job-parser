from parser.mixins import RedisCacheMixin
from parser.tests.TestAssertions import Assertions
from typing import TypeVar

import pytest
from django.http import HttpRequest

RMC = TypeVar("RMC", bound=RedisCacheMixin)


@pytest.mark.django_db
class TestRedisCacheMixin:
    """Класс описывает тестовые случаи для миксина RedisCacheMixin"""

    @pytest.mark.asyncio
    async def test_create_cache_key(
        self, cache_key: RMC, request_: HttpRequest
    ) -> None:
        """Тестирует метод создания ключа кэша.

        Args:
            cache_key (RMC): Кэш-ключ.
            request_ (HttpRequest): Запрос.
        """
        session_id = f"session_id:{request_.session.session_key}"
        Assertions.assert_compare_values(cache_key, session_id)

    @pytest.mark.asyncio
    async def test_set_data_to_cache(self, redis_mixin: RMC, cache_key: RMC) -> None:
        """Тестирует методы добавления данных в кэш и их получения.

        Args:
            redis_mixin (RMC): Экземпляр миксина.
            cache_key (RMC): Кэш-ключ.
        """
        job_list = [{"job": "test1"}, {"job": "test2"}]
        await redis_mixin.set_data_to_cache(job_list)
        result = await redis_mixin.get_data_from_cache()
        Assertions.assert_compare_values(job_list, result)
        Assertions.assert_compare_values(job_list, result)
