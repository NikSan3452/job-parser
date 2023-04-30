import datetime

import pytest
from pytest_mock import MockerFixture

from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter


@pytest.fixture
def params() -> RequestConfig:
    """Создает тестовые параметры запроса для API HeadHunter.

    Returns:
        dict: Экземпляр RequestConfig.
    """
    params = RequestConfig(
        city="Москва",
        city_from_db=1,
        job="Python",
        remote=True,
        date_from="2023-01-01",
        date_to="2023-12-31",
        experience=4,
    )
    return params


@pytest.fixture
def mock_vacancy_parsing(mocker: MockerFixture) -> list[dict]:
    hh_vacancy = [
        {
            "name": "Python",
            "area": {"id": "1", "name": "Москва"},
            "salary": {"from": 10000, "to": 20000, "currency": "USD"},
            "published_at": "2023-01-01T01:01:01+0100",
            "alternate_url": "https://example.com/vacancy/1",
            "employer": {
                "name": "Test company",
                "logo_urls": {
                    "original": "https://hhcdn.ru/employer-logo-original/951707.png",
                    "240": "https://hhcdn.ru/employer-logo/4247361.png",
                    "90": "https://hhcdn.ru/employer-logo/4247360.png",
                },
            },
            "snippet": {
                "requirement": "Test requirement",
                "responsibility": "Test responsibility",
            },
            "experience": {"id": "moreThan6", "name": "Более 6 лет"},
            "employment": {"id": "full", "name": "Полная занятость"},
        }
    ]
    mock = mocker.patch("parser.api.base_parser.Parser.get_vacancies")
    mock.return_value = hh_vacancy
    return mock


@pytest.fixture
def mock_vacancy_parsing_with_wrong_values(mocker: MockerFixture) -> dict:
    hh_vacancy = [
        {
            "name": None,
            "area": None,
            "salary": None,
            "published_at": None,
            "alternate_url": None,
            "employer": None,
            "snippet": None,
            "experience": None,
            "employment": None,
        }
    ]
    mock = mocker.patch("parser.api.base_parser.Parser.get_vacancies")
    mock.return_value = hh_vacancy
    return mock


@pytest.mark.asyncio
class TestHeadHunterPositive:
    """Класс описывает позитивные тестовые случаи для класса Headhunter.

    Этот класс содержит тесты для проверки различных позитивных сценариев при работе с
    классом Headhunter: проверка формирования параметров запроса и парсинга вакансий
    из Headhunter.
    """

    async def test_get_request_params(self, params: RequestConfig) -> None:
        """Тест проверяет формирование параметров запроса.

        Создается экземпляр класса Headhunter с указанными параметрами.
        Вызывается метод get_request_params.
        Ожидается, что метод вернет словарь с параметрами запроса, соответствующими
        указанным при создании экземпляра класса.

        Args:
            params (RequestConfig): Параметры запроса.
        """
        # Создаем экземпляр парсера с параметрами запроса
        headhunter = Headhunter(params)

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        hh_params = await headhunter.get_request_params()

        assert hh_params["text"] == "Программист"
        assert hh_params["per_page"] == 100
        assert hh_params["date_from"] == datetime.date(2023, 1, 1)
        assert hh_params["date_to"] == datetime.date(2023, 12, 31)
        assert hh_params["area"] == 1
        assert hh_params["schedule"] == "remote"
        assert hh_params["experience"] == "between3And6"

        Parser.general_job_list.clear()

    async def test_parsing_vacancy_headhunter(
        self, params: RequestConfig, mock_vacancy_parsing: dict
    ) -> None:
        """Этот тест проверяет парсинг вакансии с HeadHunter.

        В начале создает экземпляр класса Headhunter с заданными параметрами и
        вызывает метод `parsing_vacancy_headhunter`.
        Ожидается, что результат будет словарем с определенными ключами и значениями.
        Также проверяется, что длина списка `general_job_list` в классе Parser равна 1.

        Args:
            params (RequestConfig): Параметры для создания экземпляра класса Headhunter.
            mock_vacancy_parsing (dict): Мок-заглушка с информацией о вакансии.
        """
        hh = Headhunter(params)
        result = await hh.parsing_vacancy_headhunter()

        assert isinstance(result, dict)
        assert result == {
            "job_board": "HeadHunter",
            "url": "https://example.com/vacancy/1",
            "title": "Python",
            "salary_from": 10000,
            "salary_to": 20000,
            "salary_currency": "USD",
            "responsibility": "Test responsibility",
            "requirement": "Test requirement",
            "city": "Москва",
            "company": "Test company",
            "type_of_work": "Полная занятость",
            "experience": "Более 6 лет",
            "published_at": datetime.datetime.strptime(
                "2023-01-01T01:01:01+0100", "%Y-%m-%dT%H:%M:%S%z"
            ).date(),
        }
        assert len(Parser.general_job_list) == 1
        Parser.general_job_list.clear()


@pytest.mark.asyncio
class TestHeadHunterNegative:
    """Класс описывает негативные тестовые случаи для класса Headhunter.

    Этот класс содержит тесты для проверки различных негативных сценариев при работе с
    классом Headhunter: проверка парсинга вакансий из Headhunter с отсутствующими
    значениями и формирования параметров запроса с отсутствующими значениями.
    """

    async def test_get_request_params_with_none(self) -> None:
        """Тест проверяет формирование параметров запроса с отсутствующими значениями.

        Создается экземпляр класса Headhunter с отсутствующими значениями для некоторых
        параметров.
        Вызывается метод get_request_params.
        Ожидается, что метод вернет словарь с параметрами запроса, соответствующими
        указанным при создании экземпляра класса.

        """
        # Создаем тестовые параметры запроса
        data = dict(
            city=None,
            city_from_db=None,
            job=None,
            remote=False,
            date_from=None,
            date_to=None,
            experience=0,
        )
        params = RequestConfig(**data)

        # Создаем экземпляр парсера с параметрами запроса
        headhunter = Headhunter(params)

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        hh_params = await headhunter.get_request_params()

        assert hh_params["text"] is None
        assert hh_params["date_from"] == datetime.date.today() - datetime.timedelta(1)
        assert hh_params["date_to"] == datetime.date.today()
        assert "area" not in hh_params
        assert "schedule" not in hh_params
        assert "experience" not in hh_params
        assert "experience" not in hh_params

    async def test_parsing_vacancy_headhunter_wrong_values(
        self, params: RequestConfig, mock_vacancy_parsing_with_wrong_values: dict
    ) -> None:
        """Этот тест проверяет парсинг вакансии с HeadHunter с неверными значениями.

        В начале создает экземпляр класса Headhunter с заданными параметрами и
        вызывает метод `parsing_vacancy_headhunter`.
        Ожидается, что результат будет словарем с неверными значениями.
        Также проверяется, что длина списка `general_job_list` в классе Parser равна 1.

        Args:
            params (RequestConfig): Параметры для создания экземпляра класса Headhunter.
            mock_vacancy_parsing (dict): Мок-заглушка с информацией о вакансии.
        """
        hh = Headhunter(params)
        result = await hh.parsing_vacancy_headhunter()

        assert isinstance(result, dict)
        assert result == {
            "job_board": "HeadHunter",
            "url": None,
            "title": None,
            "salary_from": None,
            "salary_to": None,
            "salary_currency": None,
            "responsibility": "Нет описания",
            "requirement": "Нет описания",
            "city": None,
            "company": None,
            "type_of_work": None,
            "experience": None,
            "published_at": None,
        }
        assert len(Parser.general_job_list) == 1
        Parser.general_job_list.clear()
