import datetime
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Trudvsem
from parser.api.utils import Utils

import pytest


class TestTrudvsem:
    """Класс описывает тестовые случаи для парсера Trudvsem."""

    @pytest.fixture
    def params(self) -> RequestConfig:
        """Создает тестовые параметры запроса для API Trudvsem.

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
        """Тестирует метод формирования параметров для API Trudvsem.

        Args:
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        trudvsem = Trudvsem(params)

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        tv_params = await trudvsem.get_request_params()

        assert tv_params["text"] == "Программист"
        assert tv_params["limit"] == 100
        assert tv_params["offset"] == 0
        assert tv_params["modifiedFrom"] == await Utils.convert_date_for_trudvsem(
            "2023-01-01"
        )
        assert tv_params["modifiedTo"] == await Utils.convert_date_for_trudvsem(
            "2023-12-31"
        )
        assert tv_params[
            "experienceFrom"
        ] in await Utils.convert_experience_for_trudvsem(3)
        assert tv_params["experienceTo"] in await Utils.convert_experience_for_trudvsem(
            3
        )

    @pytest.mark.asyncio
    async def test_get_request_params_with_none(self) -> None:
        """Тестирует метод формирования параметров для API Trudvsem со значениями None."""
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
        trudvsem = Trudvsem(params)

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        tv_params = await trudvsem.get_request_params()

        date_from = datetime.date.today() - datetime.timedelta(1)
        date_to = datetime.date.today()

        assert tv_params["text"] is None
        assert tv_params["modifiedFrom"] == await Utils.convert_date_for_trudvsem(
            date_from
        )
        assert tv_params["modifiedTo"] == await Utils.convert_date_for_trudvsem(date_to)
        assert "experienceFrom" not in tv_params
        assert "experienceTo" not in tv_params

    @pytest.mark.asyncio
    async def test_get_vacancy_from_trudvsem(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API Trudvsem.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        trudvsem = Trudvsem(params)

        # Создаем фиктивные данные
        mocker.patch.object(trudvsem, "get_vacancies")
        trudvsem.get_vacancies.return_value = [
            {
                "vacancy": {
                    "vac_url": "https://trudvsem.ru/vacancy/12345",
                    "creation-date": "2023-01-01",
                    "job-name": "Программист",
                    "salary_min": 50000,
                    "salary_max": 100000,
                    "salary_currency": "RUR",
                    "duty": "обязанности",
                    "requirement": {
                        "education": "образование",
                        "experience": "опыт работы",
                    },
                    "schedule": "Неполный рабочий день",
                    "experience": {"title": "Без опыта"},
                    "addresses": {
                        "address": [{"location": "Москва"}],
                    },
                    "company": {"name": "company1"},
                }
            }
        ]

        # Вызываем метод получения вакансий из API Trudvsem
        job_dict = await trudvsem.get_vacancy_from_trudvsem()

        assert job_dict["job_board"] == "Trudvsem"
        assert job_dict["url"] == "https://trudvsem.ru/vacancy/12345"
        assert job_dict["title"] == "Программист"
        assert job_dict["salary_from"] == 50000
        assert job_dict["salary_to"] == 100000
        assert job_dict["salary_currency"] == "RUR"
        assert job_dict["responsibility"] == "обязанности"
        assert (
            job_dict["requirement"]
            == "образование образование, опыт работы (лет): опыт работы"
        )
        assert job_dict["company"] == "company1"
        assert job_dict["type_of_work"] == "Неполный рабочий день"
        assert job_dict["city"] == "Москва"
        assert job_dict["published_at"] == datetime.date(2023, 1, 1)
        assert len(Parser.general_job_list) == 1

    @pytest.mark.asyncio
    async def test_get_vacancy_from_trudvsem_with_none(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тестирует метод парсинга вакансий из API Trudvsem со значениями None.

        Args:
            mocker (_type_): Mock-фикстура.
            params (RequestConfig): Тестовые параметры.
        """
        # Создаем экземпляр парсера с параметрами запроса
        trudvsem = Trudvsem(params)

        # Создаем фиктивные данные со значениями None для проверки условий if/else
        mocker.patch.object(trudvsem, "get_vacancies")
        trudvsem.get_vacancies.return_value = [
            {
                "vacancy": {
                    "vac_url": "https://trudvsem.ru/vacancy/12345",
                    "creation-date": "2023-01-01",
                    "job-name": "Программист",
                    "salary_min": None,
                    "salary_max": None,
                    "salary_currency": None,
                    "duty": None,
                    "requirement": None,
                    "schedule": None,
                    "experience": None,
                    "addresses": None,
                    "company": None,
                }
            }
        ]

        # Вызываем метод получения вакансий из API Trudvsem
        job_dict = await trudvsem.get_vacancy_from_trudvsem()

        assert job_dict["job_board"] == "Trudvsem"
        assert job_dict["url"] == "https://trudvsem.ru/vacancy/12345"
        assert job_dict["title"] == "Программист"
        assert job_dict["salary_from"] is None
        assert job_dict["salary_to"] is None
        assert job_dict["responsibility"] == "Нет описания"
        assert job_dict["requirement"] == "Нет описания"
        assert job_dict["company"] == "Не указано"
        assert job_dict["type_of_work"] == "Не указано"
        assert job_dict["city"] == "Не указано"
        assert job_dict["published_at"] == datetime.date(2023, 1, 1)
        assert len(Parser.general_job_list) == 1