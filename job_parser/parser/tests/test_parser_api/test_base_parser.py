import json
import types
from parser.api.base_parser import CreateConnection, Parser
from parser.api.config import ParserConfig
from typing import Any, Callable

import httpx
import pytest
from loguru import logger
from pytest_mock import MockerFixture


@pytest.fixture
def mock_response(monkeypatch: Any) -> Callable:
    """Фикстура для мокирования ответа на запрос.

    Фикстура заменяет метод get у объекта httpx.AsyncClient на функцию mock_get,
    которая возвращает различные ответы в зависимости от url запроса.

    Args:
        monkeypatch (Any): Фикстура для замены атрибутов и методов.

    Returns:
        Callable: Функция mock_get для мокирования ответа на запрос.
    """

    async def mock_get(*args, **kwargs):
        if "badurl" in kwargs["url"]:
            return httpx.Response(404)
        elif "invalidurl" in kwargs["url"]:
            raise httpx.InvalidURL("Invalid URL")
        return httpx.Response(200, json={"key": "value"})

    monkeypatch.setattr(httpx.AsyncClient, "get", mock_get)


class TestCreateClientPositive:
    """
    Класс описывает позитивные тестовые случаи для метода create_client.

    Этот класс содержит тесты для проверки различных позитивных сценариев
    при вызове метода create_client: успешное выполнение запроса и установка заголовка.
    """

    @pytest.mark.asyncio
    async def test_success(self, mock_response: Callable) -> None:
        """Тест проверяет успешное выполнение запроса.

        Создается объект CreateConnection и вызывается метод create_client с
        указанными значениями url и params.
        Ожидается, что статус код ответа будет равен 200 и содержимое ответа будет
        соответствовать ожидаемому.

        Args:
            mock_response (Callable): Фикстура для мокирования ответа на запрос.
        """
        connection = CreateConnection()
        url = "https://example.com"
        params = {"key1": "value1", "key2": "value2"}
        response = await connection.create_client(url, params)
        assert response.status_code == 200
        assert response.json() == {"key": "value"}

    @pytest.mark.asyncio
    async def test_set_header(self, monkeypatch: Any) -> None:
        """Тест проверяет установку заголовка x-api-app-id.

        Создается объект CreateConnection и вызывается метод create_client
        с указанным значением url.
        Ожидается, что заголовок x-api-app-id будет установлен в значение test_key.

        Args:
            monkeypatch (Any): Фикстура для мокирования выбора ключа из списка ключей.
        """
        config = ParserConfig()
        connection = CreateConnection()
        url = config.superjob_url
        monkeypatch.setattr("random.choice", lambda x: "test_key")
        response = await connection.create_client(url)
        request_headers = response.request.headers
        assert request_headers["x-api-app-id"] == "test_key"


class TestCreateClientNegative:
    """Класс описывает негативные тестовые случаи для метода create_client.

    Этот класс содержит тесты для проверки различных негативных сценариев при
    вызове метода create_client: неудачное выполнение запроса из-за неправильного url
    и неустановленного заголовка x-api-app-id.
    """

    @pytest.mark.asyncio
    async def test_failure(self, mock_response: Callable) -> None:
        """Тест проверяет неудачное выполнение запроса из-за неправильного url.

        Создается объект CreateConnection и вызывается метод create_client
        с указанными значениями url и params.
        Ожидается, что статус код ответа будет равен 404.

        Args:
            mock_response (Callable): Фикстура для мокирования ответа на запрос.
        """
        connection = CreateConnection()
        url = "https://badurl.com"
        params = {"key1": "value1", "key2": "value2"}
        response = await connection.create_client(url, params)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_failure_invalid_url(self, mock_response: Callable) -> None:
        """Тест проверяет неудачное выполнение запроса из-за неправильного формата url.

        Создается объект CreateConnection и вызывается метод create_client
        с указанными значениями url и params.
        Ожидается возникновение ошибки InvalidURL.

        Args:
            mock_response (Callable): Фикстура для мокирования ответа на запрос.
        """
        connection = CreateConnection()
        url = "invalidurl"
        params = {"key1": "value1", "key2": "value2"}
        with pytest.raises(httpx.InvalidURL):
            await connection.create_client(url, params)

    @pytest.mark.asyncio
    async def test_not_set_header(self) -> None:
        """Тест проверяет отсутствие заголовка x-api-app-id при вызове
        метода create_client с другим url.

        Создается объект CreateConnection и вызывается метод create_client
        с указанным значением url.
        Ожидается отсутствие заголовка x-api-app-id в запросе.

        """
        connection = CreateConnection()
        url = "https://someotherurl.com"
        with pytest.raises(httpx.HTTPError):
            response = await connection.create_client(url)
            request_headers = response.request.headers
            assert "x-api-app-id" not in request_headers


class MyParser(Parser):
    async def get_request_params(self) -> dict:
        pass

    async def get_url(self, job: dict) -> str | None:
        pass

    async def get_title(self, job: dict) -> str | None:
        pass

    async def get_salary_from(self, job: dict) -> str | None:
        pass

    async def get_salary_to(self, job: dict) -> str | None:
        pass

    async def get_salary_currency(self, job: dict) -> str | None:
        pass

    async def get_responsibility(self, job: dict) -> str:
        pass

    async def get_requirement(self, job: dict) -> str:
        pass

    async def get_city(self, job: dict) -> str | None:
        pass

    async def get_company(self, job: dict) -> str | None:
        pass

    async def get_type_of_work(self, job: dict) -> str | None:
        pass

    async def get_published_at(self, job: dict) -> str | None:
        pass


@pytest.fixture
def parser() -> MyParser:
    """Фикстура возвращает экземпляр парсера.

    Returns:
        MyParser: Экземпляр парсера.
    """
    return MyParser()


@pytest.fixture
def fix_param() -> dict:
    """Фикстура возвращает параметры для тестирования.

    Returns:
        dict: Словарь с параметрами для тестирования.
    """
    fix_param = dict(
        url="https://example.com",
        params={"param1": "value1"},
        pages=2,
        items="items",
        results="results",
    )
    return fix_param


@pytest.mark.asyncio
class TestParserPositive:
    """
    Класс описывает позитивные тестовые случаи для парсера.

    Этот класс содержит тесты для проверки различных позитивных сценариев
    при работе с парсером:
    - обработка данных в случае, если API Trudvsem
    - получение данных в остальных случаях
    - общая проверка получения вакансий.
    """

    async def test_process_trudvsem_data_vacancies(self, parser: MyParser) -> None:
        """
        Тест проверяет обработку данных от trudvsem.

        Создается объект json_data с результатами.
        Ожидается, что результат будет списком длиной 2.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
        """
        json_data = {"results": {"vacancies": [{"id": 1}, {"id": 2}]}}
        items = "results"

        result = await parser.process_trudvsem_data(json_data, items)
        assert isinstance(result, list)
        assert len(result) == 2

    async def test_get_data_success(
        self, parser: MyParser, mocker: MockerFixture, fix_param: dict
    ) -> None:
        """
        Тест проверяет успешное получение данных.

        Имитация метода create_client для возврата фиктивного ответа сервера.
        Ожидается, что результат будет словарем с ключом "key" и значением "value".

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
            mocker (MockerFixture): Фикстура для создания заглушек и имитации вызовов.
            fix_param (dict): Фикстура возвращающая параметры для тестирования.
        """
        # Имитация метода create_client для возврата фиктивного ответа сервера
        dummy_response = types.SimpleNamespace(
            content=json.dumps({"key": "value"}).encode()
        )
        mocker.patch.object(
            parser.connection, "create_client", return_value=dummy_response
        )

        result = await parser.get_data(fix_param["url"], fix_param["params"])
        assert result == {"key": "value"}

    async def test_get_vacancies(
        self, parser: MyParser, mocker: MockerFixture, fix_param: dict
    ) -> None:
        """
        Тест проверяет получение вакансий.

        Имитация метода create_client для возврата фиктивных данных.
        Ожидается, что результат будет списком длиной 4.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
            mocker (MockerFixture): Фикстура для создания заглушек и имитации вызовов.
            fix_param (dict): Фикстура возвращающая параметры для тестирования.
        """
        # Имитация метода create_client для возврата фиктивных данных
        dummy_data = {"items": [{"id": 1}, {"id": 2}]}
        dummy_response = types.SimpleNamespace(content=json.dumps(dummy_data).encode())
        mocker.patch.object(
            parser.connection, "create_client", return_value=dummy_response
        )

        result = await parser.get_vacancies(
            fix_param["url"],
            fix_param["params"],
            fix_param["pages"],
            fix_param["items"],
        )
        assert isinstance(result, list)
        assert len(result) == 4


@pytest.mark.asyncio
class TestParserNegative:
    """
    Класс описывает негативные тестовые случаи для парсера.

    Этот класс содержит тесты для проверки различных негативных
    сценариев при работе с парсером:
    - обработка данных от trudvsem без элементов или с пустыми вакансиями
    - получение данных с ошибкой json или ошибкой атрибута
    - получение результат без данных.
    """

    async def test_process_trudvsem_data_no_items(self, parser: MyParser) -> None:
        """
        Тест проверяет обработку данных от trudvsem без элементов.

        Создается пустой объект json_data.
        Ожидается, что результат будет None.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
        """
        json_data = {}
        items = "results"

        result = await parser.process_trudvsem_data(json_data, items)
        assert result is None

    async def test_process_trudvsem_data_empty_vacancies(
        self, parser: MyParser
    ) -> None:
        """
        Тест проверяет обработку данных от trudvsem с пустым списком вакансий.

        Создается объект json_data с пустым списком вакансий.
        Ожидается, что результат будет пустым списком.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
        """
        json_data = {"results": {"vacancies": []}}
        items = "results"

        result = await parser.process_trudvsem_data(json_data, items)
        assert result == []

    async def test_get_data_json_error(
        self, parser: MyParser, mocker: MockerFixture, fix_param: dict
    ) -> None:
        """
        Тест проверяет получение данных с ошибкой json.

        Имитация метода create_client для возврата некорректного ответа сервера.
        Имитация метода logger.exception для проверки вызова логирования ошибки.
        Ожидается, что результат будет пустым словарем.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
            mocker (MockerFixture): Фикстура для создания заглушек и имитации вызовов.
            fix_param (dict): Фикстура возвращающая параметры для тестирования.
        """
        # Имитация метода create_client для возврата некорректного ответа сервера
        dummy_response = types.SimpleNamespace(content=b"not json")
        mocker.patch.object(
            parser.connection, "create_client", return_value=dummy_response
        )

        # Имитация метода logger.exception для проверки вызова логирования ошибки
        mocker.patch.object(logger, "exception")

        result = await parser.get_data(fix_param["url"], fix_param["params"])
        assert result == {}
        logger.exception.assert_called_once()

    async def test_get_data_attribute_error(
        self, parser: MyParser, mocker: MockerFixture, fix_param: dict
    ) -> None:
        """
        Тест проверяет получение данных с ошибкой атрибута.

        Имитация метода create_client для возврата None.
        Имитация метода logger.exception для проверки вызова логирования ошибки.
        Ожидается, что результат будет пустым словарем.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
            mocker (MockerFixture): Фикстура для создания заглушек и имитации вызовов.
            fix_param (dict): Фикстура возвращающая параметры для тестирования.
        """
        # Имитация метода create_client для возврата None
        mocker.patch.object(parser.connection, "create_client", return_value=None)

        # Имитация метода logger.exception для проверки вызова логирования ошибки
        mocker.patch.object(logger, "exception")

        result = await parser.get_data(fix_param["url"], fix_param["params"])
        assert result == {}
        logger.exception.assert_called_once()

    async def test_get_vacancies_no_data(
        self, parser: MyParser, mocker: MockerFixture, fix_param: dict
    ) -> None:
        """
        Тест проверяет получение вакансий без данных.

        Имитация метода get_data для возврата пустых данных.
        Ожидается, что результат будет пустым списком.

        Args:
            parser (MyParser): Фикстура возвращающая экземпляр парсера.
            mocker (MockerFixture): Фикстура для создания заглушек и имитации вызовов.
            fix_param (dict): Фикстура возвращающая параметры для тестирования.
        """
        # Имитация метода get_data для возврата пустых данных
        dummy_data = {}
        mocker.patch.object(parser, "get_data", return_value=dummy_data)

        result = await parser.get_vacancies(
            fix_param["url"],
            fix_param["params"],
            fix_param["pages"],
            fix_param["results"],
        )
        assert isinstance(result, list)
        assert len(result) == 0
