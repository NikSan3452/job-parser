import datetime
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Trudvsem
from parser.api.utils import Utils

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def params() -> RequestConfig:
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


@pytest.fixture
def trudvsem(params: RequestConfig) -> Trudvsem:
    """Создает экземпляр парсера Trudvsem с заданными параметрами.

    Args:
        params (RequestConfig): Экземпляр RequestConfig

    Returns:
        Trudvsem: Экземпляр Trudvsem.
    """
    sj = Trudvsem(params)
    return sj


@pytest.mark.asyncio
class TestTrudvsemPositive:
    """Класс описывает позитивные тестовые случаи для класса Trudvsem.

    Этот класс содержит тесты для проверки различных позитивных сценариев при работе с
    классом Trudvsem: проверка формирования параметров запроса и парсинга вакансий
    из Trudvsem.
    """

    async def test_get_request_params(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет формирование параметров запроса.

        Создается экземпляр класса Trudvsem с указанными параметрами.
        Вызывается метод get_request_params.
        Ожидается, что метод вернет словарь с параметрами запроса, соответствующими
        указанным при создании экземпляра класса.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """

        # Вызываем метод, который формирует параметры запроса в понятный для Trudvsem вид
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

    async def test_get_vacancy_from_trudvsem(
        self, mocker: MockerFixture, trudvsem: Trudvsem
    ) -> None:
        """Тест проверяет парсинг вакансий из API Trudvsem.

        Создается экземпляр класса Trudvsem с указанными параметрами.
        Метод get_vacancies мок-объекта возвращает список с одной вакансией.
        Вызывается метод get_vacancy_from_trudvsem.
        Ожидается, что метод вернет словарь с информацией о вакансии, соответствующей
        информации в мок-объекте.

        Args:
            mocker: Фикстура для создания мок-объектов.
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
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
        job_dict = await trudvsem.parsing_vacancy_trudvsem()

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
        assert job_dict["experience"] == "Без опыта"
        assert job_dict["city"] == "Москва"
        assert job_dict["published_at"] == datetime.date(2023, 1, 1)
        assert len(Parser.general_job_list) == 1

        Parser.general_job_list.clear()

    async def test_get_url(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения ссылки.

        Создается словарь с указанным значением поля vac_url.
        Ожидается, что метод get_url вернет ссылку, соответствующую
        указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"vac_url": "https://www.trudvsem.ru/vacancy/12345"}}
        assert await trudvsem.get_url(job) == "https://www.trudvsem.ru/vacancy/12345"

    async def test_get_title(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения названия профессии.

        Создается словарь с указанным значением поля job-name.
        Ожидается, что метод get_title вернет название профессии, соответствующее
        указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"job-name": "Test"}}
        assert await trudvsem.get_title(job) == "Test"

    async def test_get_salary_from(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения минимальной зарплаты.

        Создается словарь с указанным значением поля salary_min.
        Ожидается, что метод get_salary_from вернет значение минимальной зарплаты,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"salary_min": 100000}}
        assert await trudvsem.get_salary_from(job) == 100000

    async def test_get_salary_to(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения максимальной зарплаты.

        Создается словарь с указанным значением поля salary_max.
        Ожидается, что метод get_salary_to вернет значение максимальной зарплаты,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"salary_max": 200000}}
        assert await trudvsem.get_salary_to(job) == 200000

    async def test_get_salary_currency(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения валюты зарплаты.

        Создается словарь с указанным значением поля currency.
        Ожидается, что метод get_salary_currency вернет значение валюты зарплаты,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"currency": "RUR"}}
        assert await trudvsem.get_salary_currency(job) == "RUR"

    async def test_get_responsibility(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения описания обязанностей.

        Создается словарь с указанным значением поля duty.
        Ожидается, что метод get_responsibility вернет описание обязанностей,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"duty": "Test"}}
        assert await trudvsem.get_responsibility(job) == "Test"

    async def test_get_requirement_education_and_experience(
        self, trudvsem: Trudvsem
    ) -> None:
        """Тест проверяет корректность возвращаемого значения требований.

        Создается словарь с указанными значениями полей education и experience.
        Ожидается, что метод get_requirement вернет требования,
        соответствующие указанным при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"requirement": {"education": "Высшее", "experience": "3-6"}}}
        assert (
            await trudvsem.get_requirement(job)
            == "Высшее образование, опыт работы (лет): 3-6"
        )

    async def test_get_requirement_education_only(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения требований.

        Создается словарь с указанным значением поля education.
        Ожидается, что метод get_requirement вернет требования,
        соответствующие указанным при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"requirement": {"education": "Высшее"}}}
        assert await trudvsem.get_requirement(job) == "Высшее образование"

    async def test_get_requirement_experience_only(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения требований.

        Создается словарь с указанным значением поля experience.
        Ожидается, что метод get_requirement вернет требования,
        соответствующие указанным при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"requirement": {"experience": "3-6"}}}
        assert await trudvsem.get_requirement(job) == "опыт работы (лет): 3-6"

    async def test_get_city(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения города.

        Создается словарь с указанным значением поля location.
        Ожидается, что метод get_city вернет название города,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"addresses": {"address": [{"location": "Москва"}]}}}
        assert await trudvsem.get_city(job) == "Москва"

    async def test_get_company(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения названия компании.

        Создается словарь с указанным значением поля name.
        Ожидается, что метод get_company вернет название компании,
        соответствующее указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"company": {"name": "Test"}}}
        assert await trudvsem.get_company(job) == "Test"

    async def test_get_type_of_work(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения типа работы.

        Создается словарь с указанным значением поля schedule.
        Ожидается, что метод get_type_of_work вернет тип работы,
        соответствующий указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"schedule": "Полный день"}}
        assert await trudvsem.get_type_of_work(job) == "Полный день"

    async def test_get_experience(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемого значения требуемого опыта работы.

        Создается словарь с указанным значением поля title.
        Ожидается, что метод get_experience вернет требуемый опыт работы,
        соответствующий указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"experience": {"title": "Без опыта"}}}
        assert await trudvsem.get_experience(job) == "Без опыта"

    async def test_get_published_at(self, trudvsem: Trudvsem) -> None:
        """Тест проверяет корректность возвращаемой даты публикации.

        Создается словарь с указанным значением поля creation-date.
        Ожидается, что метод get_published_at вернет дату, соответствующую
        указанной при создании словаря.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job = {"vacancy": {"creation-date": "2023-01-01"}}
        assert await trudvsem.get_published_at(job) == datetime.date(2023, 1, 1)


@pytest.mark.asyncio
class TestTrudvsemNegative:
    """Класс описывает негативные тестовые случаи для класса Trudvsem.

    Этот класс содержит тесты для проверки различных негативных сценариев при работе с
    классом Trudvsem: проверка парсинга вакансий из Trudvsem с отсутствующими
    значениями и формирования параметров запроса с отсутствующими значениями.
    """

    async def test_get_vacancy_from_trudvsem_with_none(
        self, mocker: MockerFixture, trudvsem: Trudvsem
    ) -> None:
        """Тест проверяет парсинг вакансий из API Trudvsem с отсутствующими значениями.

        Создается экземпляр класса Trudvsem с указанными параметрами.
        Метод get_vacancies мок-объекта возвращает список с одной вакансией,
        у которой отсутствуют значения для некоторых полей.
        Вызывается метод get_vacancy_from_trudvsem.
        Ожидается, что метод вернет словарь с информацией о вакансии, соответствующей
        информации в мок-объекте.

        Args:
            mocker: Фикстура для создания мок-объектов.
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """

        # Создаем фиктивные данные со значениями None для проверки условий if/else
        mocker.patch.object(trudvsem, "get_vacancies")
        trudvsem.get_vacancies.return_value = [
            {
                "vacancy": {
                    "vac_url": None,
                    "creation-date": None,
                    "job-name": None,
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
        job_dict = await trudvsem.parsing_vacancy_trudvsem()

        assert job_dict["job_board"] == "Trudvsem"
        assert job_dict["url"] is None
        assert job_dict["title"] is None
        assert job_dict["salary_from"] is None
        assert job_dict["salary_to"] is None
        assert job_dict["responsibility"] == "Нет описания"
        assert job_dict["requirement"] == "Нет описания"
        assert job_dict["company"] is None
        assert job_dict["type_of_work"] is None
        assert job_dict["experience"] is None
        assert job_dict["city"] is None
        assert job_dict["published_at"] is None
        assert len(Parser.general_job_list) == 1

        Parser.general_job_list.clear()

    async def test_get_request_params_with_none(self) -> None:
        """Тест проверяет формирование параметров запроса с отсутствующими значениями.

        Создается экземпляр класса Trudvsem с отсутствующими значениями для некоторых
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
        trudvsem = Trudvsem(params)

        # Вызываем метод, который формирует параметры запроса в понятный для Trudvsem вид
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

    async def test_get_url(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии ссылки.

        Создается пустой словарь без поля vac_url.
        Ожидается, что метод get_url вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_url(job) is None

    async def test_get_title(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии названия профессии.

        Создается пустой словарь без поля job-name.
        Ожидается, что метод get_title вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_title(job) is None

    async def test_get_salary_from(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии минимальной зарплаты.

        Создается пустой словарь без поля salary_min.
        Ожидается, что метод get_salary_from вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_salary_from(job) is None

    async def test_get_salary_to(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии максимальной зарплаты.

        Создается пустой словарь без поля salary_max.
        Ожидается, что метод get_salary_to вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_salary_to(job) is None

    async def test_get_responsibility(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии описания обязанностей.

        Создается пустой словарь без поля duty.
        Ожидается, что метод get_responsibility вернет "Нет описания".

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_responsibility(job) == "Нет описания"
    
    async def test_get_requirement_none(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии требований.

        Создается пустой словарь без полей education и experience.
        Ожидается, что метод get_requirement вернет "Нет описания".

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_requirement(job) == "Нет описания"

    async def test_get_city(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии города.

        Создается пустой словарь без поля location.
        Ожидается, что метод get_city вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_city(job) is None

    async def test_get_company(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии названия компании.

        Создается пустой словарь без поля name.
        Ожидается, что метод get_company вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_company(job) is None

    async def test_get_type_of_work(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии типа работы.

        Создается пустой словарь без поля schedule.
        Ожидается, что метод get_type_of_work вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_type_of_work(job) is None

    async def test_get_experience(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии требуемого опыта работы.

        Создается пустой словарь без поля title.
        Ожидается, что метод get_experience вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_experience(job) is None

    async def test_get_published_at(self, trudvsem: Trudvsem) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии даты публикации.

        Создается пустой словарь без поля creation-date.
        Ожидается, что метод get_published_at вернет None.

        Args:
            trudvsem (Trudvsem): Экземпляр Trudvsem.
        """
        job: dict = {}
        assert await trudvsem.get_published_at(job) is None
