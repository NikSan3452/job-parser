import datetime
import json
from parser.api.base_parser import CreateConnection, Parser

import httpx
import pytest


@pytest.fixture
def parser() -> Parser:
    """Фикстура возвращает экземпляр парсера.

    Returns:
        Parser: Экземпляр парсера.
    """
    return Parser()


@pytest.fixture
def params() -> tuple:
    """Фикстура возвращает кортеж параметров для тестов.

    Returns:
        tuple: Кортеж параметров для тестов.
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
    """Функция-заглушка для создания сессии.

    Возвращает фиктивный ответ с данными из функции get_data.

    Args:
        connection (CreateConnection): Экземпляр соединения.
        url (str): URL-адрес для запроса.
        headers (dict | None): Заголовки запроса.
        params (dict | None): Параметры запроса.

    Returns:
        list[dict]: Фиктивный ответ с данными из функции get_data.
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


class TestCreateConnection:
    """Класс описывает тестовые случаи для создания соединения.

    Этот класс содержит тесты для проверки успешного создания сессии.
    """

    @pytest.mark.asyncio
    async def test_create_session_success(self, monkeypatch, params: tuple) -> None:
        """Тест проверяет успешное создание сессии.

        Создается соединение и используется monkeypatch для замены метода
        create_session на mock_create_session.
        Вызывается метод create_session и проверяется код ответа, заголовки и
        параметры запроса.

        Args:
            monkeypatch: Фикстура pytest для временной замены атрибутов и методов.
            params (tuple): Кортеж параметров для теста.
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


class TestParserPositive:
    """Класс описывает позитивные тестовые случаи для парсера.

    Этот класс содержит тесты для проверки получения вакансий с различными параметрами.
    """

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
        """Тест проверяет получение вакансий с различными параметрами.

        Используется monkeypatch для замены метода create_session на
        mock_create_session.
        Вызывается метод get_vacancies с различными параметрами и проверяется результат.

        Args:
            monkeypatch: Фикстура pytest для временной замены атрибутов и методов.
            params (tuple): Кортеж параметров для теста.
            parser (Parser): Экземпляр парсера.
            items (str): Параметр items для метода get_vacancies.
            expected_job_board (str): Ожидаемое значение поля job_board в первой
            вакансии.
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
            # Проверяем, что содержимое соответствует ожиданиям
            assert job_list[0]["job_board"] == expected_job_board
        else:
            assert isinstance(job_list, list)
            assert len(job_list) == 0


class TestParserNegative:
    """Класс описывает негативные тестовые случаи для парсера.

    Этот класс содержит тесты для проверки поведения парсера при возникновении
    исключений.
    """

    @pytest.mark.asyncio
    async def test_get_vacancies_with_exception(
        self, parser: Parser, params: tuple
    ) -> None:
        """Тест проверяет поведение парсера при возникновении исключений.

        Вызывается метод get_vacancies с невалидными параметрами и ожидается
        возникновение исключения.

        Args:
            parser (Parser): Экземпляр парсера.
            params (tuple): Кортеж параметров для теста.
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
