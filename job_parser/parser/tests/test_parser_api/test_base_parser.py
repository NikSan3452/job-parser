from parser.api.base_parser import CreateConnection
from parser.tests.TestAssertions import Assertions

import pytest


@pytest.mark.django_db
class TestCreateConnection:
    """Класс описывает тестовые случаи для класса CreateConnection."""

    @pytest.mark.asyncio
    async def test_create_session_success(self) -> None:
        """Тестирует метод создания запросов к API"""
        connection = CreateConnection()
        url = "http://127.0.0.1:8000"
        headers = {"Content-Type": "application/json"}
        params = {"job": "python"}
        
        response = await connection.create_session(url, headers=headers, params=params)

        Assertions.assert_status_code(response, 200)
        Assertions.assert_headers(response, "application/json")
        Assertions.assert_params(response, "job=python")
