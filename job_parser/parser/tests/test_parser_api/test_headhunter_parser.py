import datetime
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter

import pytest


@pytest.fixture
def params() -> RequestConfig:
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


class TestHeadHunterPositive:
    """Класс описывает позитивные тестовые случаи для класса Headhunter.

    Этот класс содержит тесты для проверки различных позитивных сценариев при работе с
    классом Headhunter: проверка получения параметров запроса и получения вакансий
    из Headhunter.
    """

    @pytest.mark.asyncio
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

    @pytest.mark.asyncio
    async def test_get_vacancy_from_headhunter(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тест проверяет парсинг вакансий из API Headhunter.

        Создается экземпляр класса Headhunter с указанными параметрами.
        Метод get_vacancies мок-объекта возвращает список с одной вакансией.
        Вызывается метод get_vacancy_from_headhunter.
        Ожидается, что метод вернет словарь с информацией о вакансии, соответствующей
        информации в мок-объекте.

        Args:
            mocker: Фикстура для создания мок-объектов.
            params (RequestConfig): Параметры запроса.
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

        Parser.general_job_list.clear()


class TestHeadHunterNegative:
    """Класс описывает негативные тестовые случаи для класса Headhunter.

    Этот класс содержит тесты для проверки различных негативных сценариев при работе с
    классом Headhunter: проверка получения вакансий из Headhunter с отсутствующими
    значениями и получения параметров запроса с отсутствующими значениями.
    """

    @pytest.mark.asyncio
    async def test_get_vacancy_from_headhunter_with_none(
        self, mocker, params: RequestConfig
    ) -> None:
        """Тест проверяет парсинг вакансий из API Headhunter с отсутствующими
        значениями.

        Создается экземпляр класса Headhunter с указанными параметрами.
        Метод get_vacancies мок-объекта возвращает список с одной вакансией,
        у которой отсутствуют значения для некоторых полей.
        Вызывается метод get_vacancy_from_headhunter.
        Ожидается, что метод вернет словарь с информацией о вакансии, соответствующей
        информации в мок-объекте.

        Args:
            mocker: Фикстура для создания мок-объектов.
            params (RequestConfig): Параметры запроса.
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

        Parser.general_job_list.clear()

    @pytest.mark.asyncio
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
