import datetime
import json
from parser.api.base_parser import CreateConnection, Parser

import httpx
import pytest


@pytest.fixture
def parser() -> Parser:
    """Фикстура, которая возвращает экземпляр класса Parser.

    Returns:
        Parser: Экземпляр класса Parser.
    """
    return Parser()


@pytest.fixture
def params() -> tuple:
    """Фикстура, которая создает тестовые параметры запроса.

    Returns:
        tuple: Параметры запроса.
    """
    items = None
    url = "http://127.0.0.1:8000"
    params = {
        "text": "python",
        "limit": 100,
        "offset": 0,
    }
    pages = 1
    headers = {"Content-Type": "application/json"}
    return items, url, params, pages, headers


def get_data() -> list[dict]:
    """Создает тестовые данные.
    Returns:
        list[dict]: Тестовые данные.
    """
    data = {
        "items": [
            {
                "job_board": "HeadHunter",
                "title": "python",
                "url": "http://example.com/vacancy1",
                "description": "описание",
                "company": "company1",
                "published_at": datetime.date.today().strftime("%Y-%m-%d"),
                "experience": "Без опыта",
            }
        ],
        "objects": [
            {
                "job_board": "SuperJob",
                "title": "java",
                "url": "http://example.com/vacancy2",
                "description": "описание",
                "company": "company2",
                "published_at": datetime.date.today().strftime("%Y-%m-%d"),
                "experience": "Без опыта",
            }
        ],
        "results": {
            "vacancies": [
                {
                    "job_board": "Trudvsem",
                    "title": "php",
                    "url": "http://example.com/vacancy3",
                    "description": "описание",
                    "company": "company3",
                    "published_at": datetime.date.today().strftime("%Y-%m-%d"),
                    "experience": "Без опыта",
                }
            ]
        },
    }

    return data


async def mock_create_session(
    connection: CreateConnection,
    url: str,
    headers: dict | None = None,
    params: dict | None = None,
) -> list[dict]:
    """Mock-метод, который возвращает тестовые данные для метода create_session.

    Args:
        connection (CreateConnection): Экземпляр CreateConnection, который передается
        явно при вызыве этой функции, т.к первый аргумент в методе Parser.create_connection
        это self.
        url (str): URL - адрес.
        headers (dict | None, optional): Заголовки. По-умолчанию None.
        params (dict): Параметры запроса. По-умолчанию None.
    Returns:
        list[dict]: Тестовые данные.
    """
    data = get_data()
    # Кодируем данные
    json_str = json.dumps(data)
    json_bytes = json_str.encode("utf-8")

    # создаем экземпляр класса httpx.Request
    request = httpx.Request("GET", url=url, headers=headers, params=params)

    # Создаем экземпляр класса httpx.Response
    response = httpx.Response(
        status_code=200,
        request=request,
        headers=headers,
        content=json_bytes,
    )
    return response


@pytest.mark.django_db
class TestCreateConnection:
    @pytest.mark.asyncio
    async def test_create_session_success(self, monkeypatch, params: tuple) -> None:
        """Тестирует метод создания запросов к API.

        Args:
            monkeypatch (_type_): Фикстура для фиктивных запросов.
            params (tuple): Фикстура с параметрами запроса.
        """
        # создаем экземпляр класса CreateConnection
        connection = CreateConnection()
        # используем метод setattr фикстуры monkeypatch
        monkeypatch.setattr(connection, "create_session", mock_create_session)
        # вызываем метод create_session с переданными аргументами
        # первый аргумент(connection) уже не передается неявно и должен быть указан при вызове функции
        response = await connection.create_session(
            connection, params[1], headers=params[4], params=params[2]
        )
        # проверяем, что ответ имеет статус 200
        assert response.status_code == 200
        # проверяем, что ответ имеет правильные заголовки и параметры
        assert response.request.headers["Content-Type"] == "application/json"
        assert response.request.url.query.decode() == "text=python&limit=100&offset=0"


@pytest.mark.django_db(transaction=True)
class TestParser:
    """Класс описывает тестовые случаи для класса Parser."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "items,expected_job_board",
        [
            ("items", "HeadHunter"),
            ("results", "Trudvsem"),
            ("objects", "SuperJob"),
        ],
    )
    async def test_get_vacancies(
        self,
        monkeypatch,
        params: tuple,
        parser: Parser,
        items: str,
        expected_job_board: str,
    ) -> None:
        """Тестирует метод получения вакансий.

        Args:
            monkeypatch (_type_): Фикстура для фиктивных запросов.
            params (tuple): Параметры запроса.
            parser (Parser): Экземпляр Parser.
            items (str): Ключ словаря в возвращаемых API данных.
            expected_job_board (str): Ожидаемая площадка.
        """
        # Имитируем метод создания запросов к API
        monkeypatch.setattr(CreateConnection, "create_session", mock_create_session)

        # Получаем список вакансий
        job_list = await parser.get_vacancies(
            params[1], params[2], params[3], params[4], items
        )

        if expected_job_board:
            # Проверяем, что полученный ответ является списком
            assert isinstance(job_list, list)
            # Проверяем, что список не пуст.
            assert len(job_list) > 0
            # Проверяем, что содержимое соотвествует ожиданиям
            assert job_list[0]["job_board"] == expected_job_board
        else:
            assert isinstance(job_list, list)
            assert len(job_list) == 0

    @pytest.mark.asyncio
    async def test_get_vacancies_with_exception(
        self, parser: Parser, params: tuple
    ) -> None:
        """Тестирует вызов исключения в методе получения вакансий.

        Args:
            parser (Parser): Экземпляр парсера.
            params (tuple): Параметры запроса.
        """
        with pytest.raises(Exception):
            await parser.get_vacancies(
                params[1],
                params[2],
                params[3],
                params[4],
                params[0],  # items is None
            )

        with pytest.raises(Exception):
            await parser.get_vacancies(
                "http://example.com/invalid",  # Неверный адрес
                params[2],
                params[3],
                params[4],
                "items",
            )

        with pytest.raises(Exception):
            await parser.get_vacancies(
                params[1],
                "fail",  # Неверный тип объекта параметров.
                params[3],
                params[4],
                "items",
            )

        with pytest.raises(Exception):
            await parser.get_vacancies(
                params[1],
                params[2],
                params[3],
                "fail",  # Неверный тип объекта заголовков.
                "items",
            )
