import datetime
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter

import pytest


class TestHeadHunter:
    """Класс описывает тестовые случаи для парсера HeadHunter."""

    @pytest.fixture
    def params(self) -> RequestConfig:
        """Создает тестовые параметры запроса для API HeadHunter.

        Returns:
            dict: Экземпляр RequestConfig.
        """
        params = RequestConfig(
            city="Москва",
            city_from_db=1,
            job="Программист",
            remote=True,
            date_from="2023-01-01",
            date_to="2023-12-31",
            experience=3,
        )
        return params

    @pytest.mark.asyncio
    async def test_get_request_params(self, params: RequestConfig) -> None:
        """Тестирует метод формирования параметров для API Headhunter.

        Args:
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        headhunter = Headhunter(params)

        # Вызываем метод, который фформирует параметры запроса в понятный для hh вид
        hh_params = await headhunter.get_request_params()

        assert hh_params["text"] == "Программист"
        assert hh_params["per_page"] == 100
        assert hh_params["date_from"] == datetime.date(2023, 1, 1)
        assert hh_params["date_to"] == datetime.date(2023, 12, 31)
        assert hh_params["area"] == 1
        assert hh_params["schedule"] == "remote"
        assert hh_params["experience"] == "between3And6"

    @pytest.mark.asyncio
    async def test_get_request_params_with_none(self) -> None:
        """Тестирует метод формирования параметров для API Headhunter со значениями None."""
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

        # Вызываем метод, который фформирует параметры запроса в понятный для hh вид
        hh_params = await headhunter.get_request_params()

        assert hh_params["text"] is None
        assert hh_params["date_from"] == datetime.date.today() - datetime.timedelta(1)
        assert hh_params["date_to"] == datetime.date.today()
        assert "area" not in hh_params
        assert "schedule" not in hh_params
        assert "experience" not in hh_params

    @pytest.mark.asyncio
    async def test_get_vacancy_from_headhunter(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API HeadHunter.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        headhunter = Headhunter(params)

        # Создаем фиктивные данные
        mocker.patch.object(headhunter, "get_vacancies")
        headhunter.get_vacancies.return_value = [
            {
                "name": "Программист",
                "area": {
                    "name": "Москва",
                },
                "salary": {
                    "from": 2000,
                    "to": None,
                    "currency": "EUR",
                },
                "published_at": "2023-01-01T00:00:00+0300",
                "alternate_url": "https://hh.ru/vacancy/12345",
                "employer": {
                    "name": "company1",
                },
                "snippet": {
                    "requirement": "требования",
                    "responsibility": "обязанности",
                },
                "schedule": {"name": "Полный рабочий день"},
            }
        ]

        # Вызываем метод получения вакансий из API HeadHunter
        job_dict = await headhunter.get_vacancy_from_headhunter()

        assert job_dict["job_board"] == "HeadHunter"
        assert job_dict["url"] == "https://hh.ru/vacancy/12345"
        assert job_dict["title"] == "Программист"
        assert job_dict["salary_from"] == 2000
        assert job_dict["salary_to"] is None
        assert job_dict["salary_currency"] == "EUR"
        assert job_dict["responsibility"] == "обязанности"
        assert job_dict["requirement"] == "требования"
        assert job_dict["city"] == "Москва"
        assert job_dict["company"] == "company1"
        assert job_dict["type_of_work"] == "Полный рабочий день"
        assert job_dict["published_at"] == datetime.date(2023, 1, 1)
        assert len(Parser.general_job_list) == 1

    @pytest.mark.asyncio
    async def test_get_vacancy_from_headhunter_with_none(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API HeadHunter со значениями None.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        headhunter = Headhunter(params)

        # Создаем фиктивные данные со значениями None для проверки условий if/else
        mocker.patch.object(headhunter, "get_vacancies")
        headhunter.get_vacancies.return_value = [
            {
                "name": "Программист",
                "area": {
                    "name": "Москва",
                },
                "salary": None,
                "published_at": "2023-01-01T00:00:00+0300",
                "alternate_url": "https://hh.ru/vacancy/12345",
                "employer": {
                    "name": "company1",
                },
                "snippet": None,
                "schedule": None,
            }
        ]

        job_dict = await headhunter.get_vacancy_from_headhunter()

        assert job_dict["salary_from"] is None
        assert job_dict["salary_to"] is None
        assert job_dict["requirement"] == "Нет описания"
        assert job_dict["responsibility"] == "Нет описания"
        assert job_dict["type_of_work"] == "Не указано"
