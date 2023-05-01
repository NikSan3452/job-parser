import datetime

from logger import setup_logging

from .base_parser import Parser
from .config import ParserConfig, RequestConfig
from .utils import Utils

# Логирование
setup_logging()

config = ParserConfig()
utils = Utils()


class Headhunter(Parser):
    """
    Класс для парсинга вакансий с сайта HeadHunter.

    Наследуется от класса Parser.
    Класс Headhunter предназначен для парсинга вакансий с сайта HeadHunter.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта HeadHunter.
    """

    def __init__(self, params: RequestConfig) -> None:
        """
        Инициализация экземпляра класса Headhunter.

        Attributes:
            params (RequestConfig): Параметры запроса.
            pages (int): Количество страниц для обработки.
            items (str): Ключ для получения вакансий из json_data.
            job_board (str): Название сайта для парсинга вакансий.

        Args:
            params (RequestConfig): Параметры запроса.
        """
        self.params = params
        self.pages: int = 20
        self.items: str = "items"
        self.job_board = "HeadHunter"

    async def get_request_params(self) -> dict:
        """
        Асинхронный метод для получения параметров запроса для сайта HeadHunter.

        Метод формирует словарь с параметрами запроса и возвращает его.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        hh_params = {
            "text": self.params.job,
            "per_page": 100,
            "date_from": await utils.check_date_from(self.params.date_from),
            "date_to": await utils.check_date_to(self.params.date_to),
        }

        if self.params.city_from_db:
            hh_params["area"] = self.params.city_from_db

        if self.params.remote:
            hh_params["schedule"] = "remote"

        experience = "noExperience"
        if self.params.experience > 0 and self.params.experience <= 4:
            experience = await utils.convert_experience(self.params.experience)
            hh_params["experience"] = experience

        return hh_params

    async def parsing_vacancy_headhunter(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта HeadHunter.

        Метод получает параметры запроса с помощью метода get_request_params и вызывает
        метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        hh_params = await self.get_request_params()
        return await super().vacancy_parsing(
            config.headhunter_url, hh_params, self.job_board, self.pages, self.items
        )

    async def get_url(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод возвращает значение ключа "alternate_url" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        return job.get("alternate_url", None)

    async def get_title(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод возвращает значение ключа "name" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        return job.get("name", None)

    async def get_salary_from(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод получает значение ключа "salary" из словаря job и возвращает значение
        ключа "from".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary = job.get("salary", None)
        return salary.get("from", None) if salary else None

    async def get_salary_to(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод получает значение ключа "salary" из словаря job и возвращает значение
        ключа "to".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary = job.get("salary", None)
        return salary.get("to", None) if salary else None

    async def get_salary_currency(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод получает значение ключа "salary" из словаря job и возвращает значение
        ключа "currency".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        salary = job.get("salary", None)
        return salary.get("currency", None) if salary else None

    async def get_responsibility(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации об обязанностях.

        Метод получает значение ключа "snippet" из словаря job и возвращает значение
        ключа "responsibility". Если значения нет, то возвращает строку "Нет описания".
        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Обязанности по вакансии.
        """
        snippet = job.get("snippet", None)
        return snippet.get("responsibility", None) if snippet else "Нет описания"

    async def get_requirement(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации о требованиях к кандидату.

        Метод получает значение ключа "snippet" из словаря job и возвращает значение
        ключа "requirement". Если значения нет, то возвращает строку "Нет описания".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Информация о требованиях к кандидату по вакансии.
        """
        snippet = job.get("snippet", None)
        return snippet.get("requirement", None) if snippet else "Нет описания"

    async def get_city(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "area" из словаря job и возвращает значение
        ключа "name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        area = job.get("area", None)
        return area.get("name", None) if area else None

    async def get_company(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод получает значение ключа "employer" из словаря job и возвращает значение
        ключа "name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        employer = job.get("employer", None)
        return employer.get("name", None) if employer else None

    async def get_type_of_work(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения типа работы.

        Метод получает значение ключа "employment" из словаря job и возвращает значение
        ключа "name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип работы по вакансии или None, если тип работы отсутствует.
        """
        employment = job.get("employment", None)
        return employment.get("name", None) if employment else None

    async def get_experience(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения опыта работы.

        Метод получает значение ключа "experience" из словаря job и возвращает значение
        ключа "name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Опыт работы по вакансии или None, если опыт работы отсутствует.
        """
        experience = job.get("experience", None)
        return experience.get("name", None) if experience else None

    async def get_published_at(self, job: dict) -> datetime.date | None:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Метод получает значение ключа "published_at" из словаря job и преобразует его в
        формат даты. Возвращает эту дату.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        date = job.get("published_at", None)
        return (
            datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").date()
            if date
            else None
        )


class Zarplata(Headhunter):
    """Класс для парсинга вакансий с сайта Zarplata.

    Наследуется от класса Headhunter.
    Класс Zarplata предназначен для парсинга вакансий с сайта Zarplata.
    Он содержит метод parsing_vacancy_zarplata для выполнения парсинга вакансий с
    этого сайта.
    Остальные методы наследуются от родительского класса Headhunter.
    """

    def __init__(self, params: RequestConfig) -> None:
        """
        Инициализация экземпляра класса Zarplata.

        Attributes:
            job_board (str): Название сайта для парсинга вакансий.

        Args:
            params (RequestConfig): Параметры запроса.
        """
        super().__init__(params)
        self.job_board = "Zarplata"

    async def parsing_vacancy_zarplata(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта Zarplata.

        Метод получает параметры запроса с помощью метода get_request_params и вызывает
        метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        zp_params = await self.get_request_params()
        return await super().vacancy_parsing(
            config.zarplata_url, zp_params, self.job_board, self.pages, self.items
        )


class SuperJob(Parser):
    """
    Класс для парсинга вакансий с сайта SuperJob.

    Наследуется от класса Parser.
    Класс SuperJob предназначен для парсинга вакансий с сайта SuperJob.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта SuperJob.
    """

    def __init__(self, params: RequestConfig) -> None:
        """
        Инициализация экземпляра класса SuperJob.

        Attributes:
            params (RequestConfig): Параметры запроса.
            pages (int): Количество страниц для обработки.
            items (str): Ключ для получения вакансий из json_data.
            job_board (str): Название сайта для парсинга вакансий.

        Args:
            params (RequestConfig): _description_
        """
        self.params = params
        self.job_board = "SuperJob"
        self.pages = 5
        self.items = "objects"

    async def get_request_params(self) -> dict:
        """
        Асинхронный метод для получения параметров запроса для сайта SuperJob.

        Метод формирует словарь с параметрами запроса и возвращает его.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        date_from = await utils.check_date_from(self.params.date_from)
        date_to = await utils.check_date_to(self.params.date_to)

        sj_params = {
            "keyword": self.params.job,
            "count": 100,
            "date_published_from": await utils.convert_date(date_from),
            "date_published_to": await utils.convert_date(date_to),
        }

        if self.params.city:
            sj_params["town"] = self.params.city

        if self.params.remote:
            sj_params["place_of_work"] = 2

        if self.params.experience > 0 and self.params.experience <= 4:
            sj_params["experience"] = self.params.experience

        return sj_params

    async def parsing_vacancy_superjob(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта SuperJob.

        Метод получает параметры запроса с помощью метода get_request_params и вызывает
        метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        sj_params = await self.get_request_params()
        return await super().vacancy_parsing(
            config.superjob_url, sj_params, self.job_board, self.pages, self.items
        )

    async def get_url(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод возвращает значение ключа "link" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        return job.get("link", None)

    async def get_title(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод возвращает значение ключа "profession" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        return job.get("profession", None)

    async def get_salary_from(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод возвращает значение ключа "payment_from" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        return job.get("payment_from", None)

    async def get_salary_to(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод возвращает значение ключа "payment_to" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        return job.get("payment_to", None)

    async def get_salary_currency(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод возвращает значение ключа "currency" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        return job.get("currency", None)

    async def get_responsibility(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации об обязанностях.

        Метод возвращает значение ключа "work" из словаря job. Если значения нет,
        то возвращает строку "Нет описания".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Обязанности по вакансии.
        """
        return job.get("work", None) if job.get("work", None) else "Нет описания"

    async def get_requirement(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации о требованиях к кандидату.

        Метод возвращает значение ключа "candidat" из словаря job. Если значения нет,
        то возвращает строку "Нет описания".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Информация о требованиях к кандидату по вакансии.
        """
        return job.get("candidat", None) if job.get("candidat") else "Нет описания"

    async def get_city(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "town" из словаря job и возвращает значение
        ключа "title".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        town = job.get("town", None)
        return town.get("title", None) if town else None

    async def get_company(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод возвращает значение ключа "firm_name" из словаря job.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        return job.get("firm_name", None)

    async def get_type_of_work(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения типа работы.

        Метод получает значение ключа "type_of_work" из словаря job и возвращает
        значение ключа "title".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип работы по вакансии или None, если тип работы отсутствует.
        """
        type_of_work = job.get("type_of_work", None)
        return type_of_work.get("title", None) if type_of_work else None

    async def get_experience(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения опыта работы.

        Метод получает значение ключа "experience" из словаря job и возвращает
        значение ключа "title".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Опыт работы по вакансии или None, если опыт работы отсутствует.
        """
        experience = job.get("experience", None)
        return experience.get("title", None) if experience else None

    async def get_published_at(self, job: dict) -> datetime.date | None:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Метод получает значение ключа "date_published" из словаря job и преобразует его
        в формат даты. Возвращает эту дату.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        date = job.get("date_published", None)
        return datetime.date.fromtimestamp(date) if date else None


class Trudvsem(Parser):
    """
    Класс для парсинга вакансий с сайта Trudvsem.

    Наследуется от класса Parser.
    Класс Trudvsem предназначен для парсинга вакансий с сайта Trudvsem.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта Trudvsem.
    """

    def __init__(self, params: RequestConfig) -> None:
        """
        Инициализация экземпляра класса Trudvsem.

        Attributes:
            params (RequestConfig): Параметры запроса.
            pages (int): Количество страниц для обработки.
            items (str): Ключ для получения вакансий из json_data.
            job_board (str): Название сайта для парсинга вакансий.

        Args:
            params (RequestConfig): Параметры запроса.
        """
        self.params = params
        self.job_board = "Trudvsem"
        self.pages = 20
        self.items = "results"

    async def get_request_params(self) -> dict:
        """
        Асинхронный метод для получения параметров запроса для сайта Trudvsem.

        Метод формирует словарь с параметрами запроса и возвращает его.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        date_from = await utils.check_date_from(self.params.date_from)
        date_to = await utils.check_date_to(self.params.date_to)

        tv_params = {
            "text": self.params.job,
            "limit": 100,
            "offset": 0,
            "modifiedFrom": await utils.convert_date_for_trudvsem(date_from),
            "modifiedTo": await utils.convert_date_for_trudvsem(date_to),
        }

        if self.params.experience > 0 and self.params.experience <= 4:
            (
                tv_params["experienceFrom"],
                tv_params["experienceTo"],
            ) = await utils.convert_experience_for_trudvsem(self.params.experience)

        return tv_params

    async def parsing_vacancy_trudvsem(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта Trudvsem.

        Метод получает параметры запроса с помощью метода get_request_params и вызывает
        метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        tv_params = await self.get_request_params()
        return await super().vacancy_parsing(
            config.trudvsem_url, tv_params, self.job_board, self.pages, self.items
        )

    async def get_url(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "vac_url".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        vacancy = job.get("vacancy", None)
        return vacancy.get("vac_url", None) if vacancy else None

    async def get_title(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "job-name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        vacancy = job.get("vacancy", None)
        return vacancy.get("job-name", None) if vacancy else None

    async def get_salary_from(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "salary_min".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        vacancy = job.get("vacancy", None)
        return vacancy.get("salary_min", None) if vacancy else None

    async def get_salary_to(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "salary_max".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        vacancy = job.get("vacancy", None)
        return vacancy.get("salary_max", None) if vacancy else None

    async def get_salary_currency(self, job: dict) -> str:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод возвращает строку "RUR".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Валюта зарплаты по вакансии.
        """
        salary_currency = "RUR"
        return salary_currency

    async def get_responsibility(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации об обязанностях.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "duty". Если значения нет, то возвращает строку
        "Нет описания".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Обязанности по вакансии.
        """
        duty = job.get("vacancy", {}).get("duty")
        return duty if duty is not None else "Нет описания"

    async def get_requirement(self, job: dict) -> str:
        """
        Асинхронный метод для получения информации о требованиях к кандидату.

        Метод получает значение ключа "vacancy" из словаря job и формирует строку с
        требованиями к кандидату. Если значения нет, то возвращает строку
        "Нет описания".

        Метод проверяет наличие значения ключа "requirement" в словаре vacancy. Если
        значение присутствует, то метод проверяет наличие значений ключей "education" и
        "experience" в словаре vacancy["requirement"]. Если оба значения присутствуют,
        то метод формирует строку requirement с требованиями к кандидату, содержащую
        информацию об образовании и опыте работы. Если присутствует только значение
        ключа "education", то метод формирует строку requirement с требованием об
        образовании.
        Если присутствует только значение ключа "experience", то метод формирует строку
        requirement с требованием об опыте работы. Если ни одно из значений
        не присутствует, то метод устанавливает значение переменной requirement равным
        "Нет описания".
        Возвращает значение переменной requirement.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Информация о требованиях к кандидату по вакансии.
        """
        vacancy = job.get("vacancy", None)
        requirement = None
        if vacancy and vacancy.get("requirement"):
            education = vacancy["requirement"].get("education")
            experience = vacancy["requirement"].get("experience")
            if education and experience:
                requirement = (
                    f"{education} образование, опыт работы (лет): {experience}"
                )
            elif education:
                requirement = f"{education} образование"
            elif experience:
                requirement = f"опыт работы (лет): {experience}"
            else:
                requirement = "Нет описания"
        else:
            requirement = "Нет описания"
        return requirement

    async def get_city(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "location".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        vacancy = job.get("vacancy", None)
        addresses = vacancy.get("addresses") if vacancy else None
        return vacancy["addresses"]["address"][0]["location"] if addresses else None

    async def get_company(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "name".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        vacancy = job.get("vacancy", None)
        company = vacancy.get("company") if vacancy else None
        return company.get("name", None) if company else None

    async def get_type_of_work(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения типа занятости.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "schedule".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип занятости по вакансии или None, если тип занятости
            отсутствует.
        """
        vacancy = job.get("vacancy", None)
        return vacancy.get("schedule", None) if vacancy else None

    async def get_experience(self, job: dict) -> str | None:
        """
        Асинхронный метод для получения опыта работы.

        Метод получает значение ключа "experience" из словаря job и возвращает
        значение ключа "title".

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Опыт работы по вакансии или None, если опыт работы отсутствует.
        """
        vacancy = job.get("vacancy", None)
        if vacancy:
            experience = vacancy.get("experience", {})
            if experience:
                return experience.get("title", None)
        return None

    async def get_published_at(self, job: dict) -> datetime.date | None:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Метод получает значение ключа "vacancy" из словаря job и возвращает значение
        ключа "creation-date". Преобразует его в формат даты и
        возвращает эту дату.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        vacancy = job.get("vacancy", None)
        date = vacancy.get("creation-date", None) if vacancy else None
        return datetime.datetime.strptime(date, "%Y-%m-%d").date() if date else None
