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
def headhunter(params: RequestConfig) -> Headhunter:
    """Создает экземпляр парсера HeadHunter с заданными параметрами.

    Args:
        params (RequestConfig): Экземпляр RequestConfig

    Returns:
        Headhunter: Экземпляр HeadHunter.
    """
    hh = Headhunter(params)
    return hh


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

    async def test_get_request_params(self, headhunter: Headhunter) -> None:
        """Тест проверяет формирование параметров запроса.

        Создается экземпляр класса Headhunter с указанными параметрами.
        Вызывается метод get_request_params.
        Ожидается, что метод вернет словарь с параметрами запроса, соответствующими
        указанным при создании экземпляра класса.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """

        # Вызываем метод, который формирует параметры запроса в понятный для hh вид
        hh_params = await headhunter.get_request_params()

        assert hh_params["text"] == "Python"
        assert hh_params["per_page"] == 100
        assert hh_params["date_from"] == datetime.date(2023, 1, 1)
        assert hh_params["date_to"] == datetime.date(2023, 12, 31)
        assert hh_params["area"] == 1
        assert hh_params["schedule"] == "remote"
        assert hh_params["experience"] == "moreThan6"

        Parser.general_job_list.clear()

    async def test_parsing_vacancy_headhunter(
        self, headhunter: Headhunter, mock_vacancy_parsing: dict
    ) -> None:
        """Этот тест проверяет парсинг вакансии с HeadHunter.

        В начале создает экземпляр класса Headhunter с заданными параметрами и
        вызывает метод `parsing_vacancy_headhunter`.
        Ожидается, что результат будет словарем с определенными ключами и значениями.
        Также проверяется, что длина списка `general_job_list` в классе Parser равна 1.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
            mock_vacancy_parsing (dict): Мок-заглушка с информацией о вакансии.
        """
        result = await headhunter.parsing_vacancy_headhunter()

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

    async def test_get_url(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля alternate_url.

        Создается словарь с полем alternate_url.
        Ожидается, что метод get_url вернет значение этого поля.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"alternate_url": "https://example.com"}
        assert await headhunter.get_url(job) == "https://example.com"

    async def test_get_title(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля name.

        Создается словарь с полем name.
        Ожидается, что метод get_title вернет значение этого поля.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"name": "Test"}
        assert await headhunter.get_title(job) == "Test"

    async def test_get_salary_from(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля salary и from.

        Создается словарь с полем salary и вложенным полем from.
        Ожидается, что метод get_salary_from вернет значение поля from.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"salary": {"from": 1000}}
        assert await headhunter.get_salary_from(job) == 1000

    async def test_get_salary_to(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля salary и to.

        Создается словарь с полем salary и вложенным полем to.
        Ожидается, что метод get_salary_to вернет значение поля to.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"salary": {"to": 2000}}
        assert await headhunter.get_salary_to(job) == 2000

    async def test_get_salary_currency(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля salary и currency.

        Создается словарь с полем salary и вложенным полем currency.
        Ожидается, что метод get_salary_currency вернет значение поля currency.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"salary": {"currency": "USD"}}
        assert await headhunter.get_salary_currency(job) == "USD"

    async def test_get_responsibility(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля snippet и responsibility.

        Создается словарь с полем snippet и вложенным полем responsibility.
        Ожидается, что метод get_responsibility вернет значение поля responsibility.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"snippet": {"responsibility": "Test"}}
        assert await headhunter.get_responsibility(job) == "Test"

    async def test_get_requirement(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля snippet и requirement.

        Создается словарь с полем snippet и вложенным полем requirement.
        Ожидается, что метод get_requirement вернет значение поля requirement.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"snippet": {"requirement": "Test"}}
        assert await headhunter.get_requirement(job) == "Test"

    async def test_get_city(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля area и name.

        Создается словарь с полем area и вложенным полем name.
        Ожидается, что метод get_city вернет значение поля name.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"area": {"name": "Москва"}}
        assert await headhunter.get_city(job) == "Москва"

    async def test_get_company(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля employer и name.

        Создается словарь с полем employer и вложенным полем name.
        Ожидается, что метод get_company вернет значение поля name.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"employer": {"name": "Test"}}
        assert await headhunter.get_company(job) == "Test"

    async def test_get_type_of_work(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля employment и name.

        Создается словарь с полем employment и вложенным полем name.
        Ожидается, что метод get_type_of_work вернет значение поля name.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"employment": {"name": "Полная занятость"}}
        assert await headhunter.get_type_of_work(job) == "Полная занятость"

    async def test_get_experience(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при наличии поля experience и name.

        Создается словарь с полем experience и вложенным полем name.
        Ожидается, что метод get_experience вернет значение поля name.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {"experience": {"name": "Более 6 лет"}}
        assert await headhunter.get_experience(job) == "Более 6 лет"

    async def test_get_published_at(self, headhunter: Headhunter) -> None:
        """Тест проверяет корректность возвращаемой даты публикации.

        Создается словарь с указанным значением поля published_at.
        Ожидается, что метод get_published_at вернет дату, соответствующую
        указанной при создании словаря.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job = {"published_at": "2023-01-01T01:01:01+00:00"}
        assert (
            await headhunter.get_published_at(job)
            == datetime.datetime(2023, 1, 1).date()
        )


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
        self, headhunter: Headhunter, mock_vacancy_parsing_with_wrong_values: dict
    ) -> None:
        """Этот тест проверяет парсинг вакансии с HeadHunter с неверными значениями.

        В начале создает экземпляр класса Headhunter с заданными параметрами и
        вызывает метод `parsing_vacancy_headhunter`.
        Ожидается, что результат будет словарем с неверными значениями.
        Также проверяется, что длина списка `general_job_list` в классе Parser равна 1.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
            mock_vacancy_parsing (dict): Мок-заглушка с информацией о вакансии.
        """
        result = await headhunter.parsing_vacancy_headhunter()

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

    async def test_get_url_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля alternate_url.

        Создается пустой словарь без поля alternate_url.
        Ожидается, что метод get_url вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_url(job) is None

    async def test_get_title_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля name.

        Создается пустой словарь без поля name.
        Ожидается, что метод get_title вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_title(job) is None

    async def test_get_salary_from_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля salary.

        Создается пустой словарь без поля salary.
        Ожидается, что метод get_salary_from вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_salary_from(job) is None

    async def test_get_salary_to_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля salary.

        Создается пустой словарь без поля salary.
        Ожидается, что метод get_salary_to вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_salary_to(job) is None

    async def test_get_salary_currency_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля salary.

        Создается пустой словарь без поля salary.
        Ожидается, что метод get_salary_currency вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_salary_currency(job) is None

    async def test_get_responsibility_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля snippet.

        Создается пустой словарь без поля snippet.
        Ожидается, что метод get_responsibility вернет "Нет описания".

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_responsibility(job) == "Нет описания"

    async def test_get_requirement_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля snippet.

        Создается пустой словарь без поля snippet.
        Ожидается, что метод get_requirement вернет "Нет описания".

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_requirement(job) == "Нет описания"

    async def test_get_city_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля area.

        Создается пустой словарь без поля area.
        Ожидается, что метод get_city вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_city(job) is None

    async def test_get_company_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля employer.

        Создается пустой словарь без поля employer.
        Ожидается, что метод get_company вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_company(job) is None

    async def test_get_type_of_work_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля employment.

        Создается пустой словарь без поля employment.
        Ожидается, что метод get_type_of_work вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_type_of_work(job) is None

    async def test_get_experience_none(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии поля experience.

        Создается пустой словарь без поля experience.
        Ожидается, что метод get_experience вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_experience(job) is None

    async def test_get_published_at(self, headhunter: Headhunter) -> None:
        """
        Тест проверяет корректность возвращаемого значения
        при отсутствии даты публикации.

        Создается пустой словарь без поля published_at.
        Ожидается, что метод get_published_at вернет None.

        Args:
            headhunter (Headhunter): Экземпляр Headhunter.
        """
        job: dict = {}
        assert await headhunter.get_published_at(job) is None
