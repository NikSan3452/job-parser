import datetime
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import SuperJob
from parser.api.utils import Utils

import pytest


class TestSuperJob:
    """Класс описывает тестовые случаи для парсера SuperJob."""

    @pytest.fixture
    def params(self) -> RequestConfig:
        """Создает тестовые параметры запроса для API SuperJob.

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
        """Тестирует метод формирования параметров для API SuperJob.

        Args:
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        superjob = SuperJob(params)

        # Вызываем метод, который формирует параметры запроса в понятный для superjob вид
        sj_params = await superjob.get_request_params()

        assert sj_params["keyword"] == "Программист"
        assert sj_params["count"] == 100
        assert sj_params["date_published_from"] == await Utils.convert_date(
            "2023-01-01"
        )
        assert sj_params["date_published_to"] == await Utils.convert_date("2023-12-31")
        assert sj_params["town"] == "Москва"
        assert sj_params["place_of_work"] == 2
        assert sj_params["experience"] == 3

    @pytest.mark.asyncio
    async def test_get_request_params_with_none(self) -> None:
        """Тестирует метод формирования параметров для API SuperJob со значениями None."""
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
        superjob = SuperJob(params)

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        sj_params = await superjob.get_request_params()

        date_from = datetime.date.today() - datetime.timedelta(1)
        date_to = datetime.date.today()

        assert sj_params["keyword"] is None
        assert sj_params["date_published_from"] == await Utils.convert_date(date_from)
        assert sj_params["date_published_to"] == await Utils.convert_date(date_to)
        assert "town" not in sj_params
        assert "place_of_work" not in sj_params
        assert "experience" not in sj_params

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
    async def test_get_vacancy_from_superjob(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API SuperJob.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        superjob = SuperJob(params)

        # Создаем фиктивные данные
        mocker.patch.object(superjob, "get_vacancies")
        superjob.get_vacancies.return_value = [
            {
                "link": "https://superjob.ru/vacancy/12345",
                "date_published": await Utils.convert_date("2023-03-01"),
                "profession": "Программист",
                "payment_from": 50000,
                "payment_to": 100000,
                "currency": "rub",
                "work": "обязанности",
                "candidat": "требования",
                "type_of_work": {"title": "Неполный рабочий день"},
                "place_of_work": {"title": "Удалённая работа (на дому)"},
                "experience": {"title": "Без опыта"},
                "town": {
                    "title": "Москва",
                },
                "firm_name": "company1",
            }
        ]

        # Вызываем метод получения вакансий из API SuperJob
        job_dict = await superjob.get_vacancy_from_superjob()

        assert job_dict["job_board"] == "SuperJob"
        assert job_dict["url"] == "https://superjob.ru/vacancy/12345"
        assert job_dict["title"] == "Программист"
        assert job_dict["salary_from"] == 50000
        assert job_dict["salary_to"] == 100000
        assert job_dict["salary_currency"] == "rub"
        assert job_dict["responsibility"] == "обязанности"
        assert job_dict["requirement"] == "требования"
        assert job_dict["city"] == "Москва"
        assert job_dict["company"] == "company1"
        assert job_dict["type_of_work"] == "Неполный рабочий день"
        assert job_dict["published_at"] == datetime.date(2023, 3, 1)
        assert len(Parser.general_job_list) == 1

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
    async def test_get_vacancy_from_superjob_with_none(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API SuperJob со значениями None.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        superjob = SuperJob(params)

        # Создаем фиктивные данные со значениями None для проверки условий if/else
        mocker.patch.object(superjob, "get_vacancies")
        superjob.get_vacancies.return_value = [
            {
                "link": "https://superjob.ru/vacancy/12345",
                "date_published": await Utils.convert_date("2023-03-01"),
                "profession": "Программист",
                "payment_from": None,
                "payment_to": None,
                "currency": None,
                "work": None,
                "candidat": None,
                "type_of_work": None,
                "place_of_work": None,
                "experience": None,
                "town": None,
                "firm_name": None,
            }
        ]

        # Вызываем метод получения вакансий из API SuperJob
        job_dict = await superjob.get_vacancy_from_superjob()

        assert job_dict["job_board"] == "SuperJob"
        assert job_dict["url"] == "https://superjob.ru/vacancy/12345"
        assert job_dict["title"] == "Программист"
        assert job_dict["salary_from"] is None
        assert job_dict["salary_to"] is None
        assert job_dict["salary_currency"] == "Валюта не указана"
        assert job_dict["responsibility"] == "Нет описания"
        assert job_dict["requirement"] == "Нет описания"
        assert job_dict["city"] == "Не указано"
        assert job_dict["company"] == "Не указано"
        assert job_dict["type_of_work"] == "Не указано"
        assert job_dict["place_of_work"] == "Нет описания"
        assert job_dict["experience"] == "Не указано"
        assert job_dict["published_at"] == datetime.date(2023, 3, 1)
        assert len(Parser.general_job_list) == 1

        Parser.general_job_list.clear()