import abc
from dataclasses import dataclass
import datetime
import json
from parser.models import Vacancies
from parser.parsing.config import ParserConfig
from parser.parsing.connection import Session

from logger import logger, setup_logging

# Логирование
setup_logging()

@dataclass
class Vacancy:
    job_board: str
    url: str
    title: str
    salary_from: int
    salary_to: int
    salary_currency: str
    city: str
    company: str
    employment: str
    experience: str
    published_at: str
    description: str = ""
    schedule: str = ""
    remote: bool = False

class Parser(abc.ABC):
    """
    Базовый класс парсера вакансий.

    Наследуется от абстрактного базового класса abc.ABC.

    Класс Parser предназначен для парсинга вакансий с различных сайтов.
    Он содержит абстрактные методы для получения информации о вакансиях, такие как
    URL-адрес, название, зарплата, город и другие. Эти методы должны быть реализованы в
    дочерних классах для каждого сайта индивидуально.

    Attributes:
        session (Session): Экземпляр класса Session для создания
        соединения с API.
    """

    session = Session()

    def __init__(self, config: ParserConfig, parser: str) -> None:
        self.config = config
        self.parser = parser

        self.job_board = getattr(config, f"{parser}_job_board")
        self.url = getattr(config, f"{parser}_url")
        self.params = getattr(config, f"{parser}_params")
        self.pages = getattr(config, f"{parser}_pages")
        self.items = getattr(config, f"{parser}_items")

    async def vacancy_parsing(self) -> Vacancy:
        """
        Асинхронный метод для парсинга вакансий.

        Получает список вакансий с помощью метода `get_vacancies`, 
        затем для каждой вакансии из списка создает объект `Vacancy` с
        деталями конкретной вакансии.
        Сформированный объект добавляется в базу данных с помощью 
        метода `add_vacancy_to_database`. 
        В конце работы метода выводится сообщение о завершении сбора вакансий 
        с указанием источника.

        Returns:
            vacancy_data (Vacancy): Объект с данными о вакансии.
        """
        vacancy_list: list[dict] = await self.get_vacancies()

        for vacancy in vacancy_list:
            vacancy_data = Vacancy(
                job_board=self.job_board,
                url=await self.get_url(vacancy),
                title=await self.get_title(vacancy),
                salary_from=await self.get_salary_from(vacancy),
                salary_to=await self.get_salary_to(vacancy),
                salary_currency=await self.get_salary_currency(vacancy),
                city=await self.get_city(vacancy),
                company=await self.get_company(vacancy),
                employment=await self.get_employment(vacancy),
                experience=await self.get_experience(vacancy),
                published_at=await self.get_published_at(vacancy)
            )

            await self.update_vacancy_data(vacancy, vacancy_data)
            await self.add_vacancy_to_database(vacancy_data)

        logger.debug(f"Сбор вакансий с {self.job_board} завершен")

        return vacancy_data
    
    async def update_vacancy_data(self, vacancy: dict, vacancy_data: Vacancy) -> None:
        """
        Асинхронный метод для обновления данных о вакансии.

        Метод принимает на вход словарь `vacancy` и объект `Vacancy` с данными 
        о вакансии. В зависимости от значения атрибута `job_board`, метод обновляет 
        данные о разными способами. Если значение атрибута `job_board` равно
        "HeadHunter" или "Zarplata", то метод получает детали вакансии с помощью метода 
        `get_vacancy_details`, затем получает описание вакансии с помощью метода 
        `get_description`, график работы с помощью метода `get_schedule`, а также 
        удаленную работу с помощью метода `get_remote`. Полученные данные затем 
        сохраняются в соответствующие атрибуты объекта `Vacancy`. Если значение атрибута
        `job_board` равно "SuperJob" или "Trudvsem", то метод получает описание 
        вакансии, график работы и удаленную работу непосредственно из словаря с данными 
        о вакансии с помощью методов `get_description`, `get_schedule` и `get_remote` 
        соответственно. Полученные данные также сохраняются в соответствующие атрибуты 
        объекта `Vacancy`.

        Args:
            vacancy (dict): Словарь с данными о вакансии.
            vacancy_data (Vacancy): Объект с данными о вакансии.

        Returns:
            None
        """
        if self.job_board in ("HeadHunter", "Zarplata"):
            details = await self.get_vacancy_details(vacancy)
            description = await self.get_description(details)
            schedule = await self.get_schedule(details)
            remote = await self.get_remote(schedule)

            vacancy_data.description = description
            vacancy_data.schedule = schedule
            vacancy_data.remote = remote

        elif self.job_board in ("SuperJob", "Trudvsem"):
            vacancy_data.description = await self.get_description(vacancy)
            vacancy_data.schedule = await self.get_schedule(vacancy)
            vacancy_data.remote = await self.get_remote(vacancy_data.schedule)

    async def get_vacancy_details(self, vacancy: dict) -> dict:
        """
        Асинхронный метод для получения деталей вакансии.

        Метод принимает на вход словарь с данными о вакансии и возвращает словарь 
        с деталями конкретной вакансии. Метод получает идентификатор вакансии из словаря
        с данными с помощью метода `get_data`. Для регулирования количества запросов в 
        секунду устанавливается задержка с помощью метода `set_delay`. Полученные данные
        возвращаются, как результат работы метода. 

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            details (dict): Словарь с деталями вакансии.
        """
        vacancy_id = vacancy.get("id", None)
        if vacancy_id:
            await self.config.set_delay()
            details = await self.get_data(f"{self.url}/{vacancy_id}")
        return details

    async def add_vacancy_to_database(self, vacancy_data: Vacancy) -> None:
        try:
            await Vacancies.objects.aget_or_create(**vacancy_data.__dict__)
        except Exception as exc:
            logger.exception(exc)

    async def get_vacancies(self) -> list[dict]:
        """
        Асинхронный метод для получения списка вакансий.

        Метод возвращает список словарей с данными о вакансиях. Метод проходит по всем 
        страницам с вакансиями (количество страниц задается атрибутом `pages`), получает
        данные о вакансиях с помощью метода `get_data`, обрабатывает полученные данные 
        с помощью метода `process_data` и добавляет их в список вакансий. 
        Если обработанные данные равны `None`, то цикл прерывается. В конце каждой 
        итерации цикла значение параметра `offset` или `page` 
        (в зависимости от значения атрибута `items`) увеличивается на 1. 
        В конце работы метода возвращается список вакансий.

        Returns:
            vacancy_list(list[dict]): Список словарей с данными о вакансиях.
        """
        vacancy_list: list[dict] = []

        for page in range(self.pages):
            json_data = await self.get_data(self.url)
            vacancies = await self.process_data(json_data)
            if vacancies is None:
                break
            else:
                vacancy_list.extend(vacancies)
            page += 1
            self.params["offset" if self.items == "results" else "page"] = page
        return vacancy_list

    async def get_data(self, url: str) -> dict:
        """
        Асинхронный метод для получения данных с указанного URL.

        Метод принимает на вход URL-адрес и возвращает словарь с данными. 
        Создает соединение с помощью метода `create_client` объекта `session`, передавая
        ему URL-адрес и параметры запроса (атрибут `params`). Затем метод получает 
        содержимое ответа, декодирует его и преобразует в словарь с помощью модуля 
        `json`. Полученный словарь возвращается как результат работы метода. Если во 
        время работы метода возникает исключение, то оно логируется с помощью метода 
        `exception` объекта `logger`, а метод возвращает пустой словарь.

        Args:
            url (str): URL для получения данных.

        Returns:
            dict: Словарь с данными.
        """
        try:
            response = await self.session.create_client(url, self.params)
            data = response.content.decode()
            json_data = json.loads(data)
            return json_data
        except Exception as exc:
            logger.exception(exc)
            return {}

    async def process_data(self, json_data: dict) -> list[dict] | None:
        """
        Асинхронный метод для обработки данных, полученных с указанного URL.

        Метод проверяет значение параметра items. Если items равен None, вернется None.
        Если items равен 'results', то попытается получить вакансии по ключу
        'vacancies'.
        Иначе вернет данные по ключу 'items'.
        Args:
            json_data (dict): Словарь с данными для обработки.
            items (str | None): Ключ для получения данных из словаря json_data.

        Returns:
            list[dict] | None: Список словарей с информацией о вакансиях или None,
            если данные отсутствуют.
        """
        data = json_data.get(self.items, None)
        if data is None or len(data) == 0:
            return None
        elif self.items == "results":
            return json_data[self.items]["vacancies"]
        else:
            return data

    @abc.abstractmethod
    async def get_url(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения URL-адреса вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_title(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения названия вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_from(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения минимальной зарплаты.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_to(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения максимальной зарплаты.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_currency(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения валюты зарплаты.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_description(self, vacancy: dict) -> str:
        """
        Абстрактный асинхронный метод для получения описания вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str: Информация о вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_city(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения города.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_company(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения названия компании.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_employment(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения типа занятости.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип занятости по вакансии или None, если тип занятости
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_schedule(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения графика работы.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: График работы по вакансии или None, если график работы
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_remote(self) -> bool:
        """
        Абстрактный асинхронный метод для получения удаленной работы.

        Returns:
            bool: Удаленная работа.
        """
        pass

    @abc.abstractmethod
    async def get_experience(self, vacancy: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения опыта работы.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Требуемый опыт работы по вакансии или None, если опыт работы
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_published_at(self, vacancy: dict) -> datetime.date | None:
        """
        Абстрактный асинхронный метод для получения даты публикации вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Дата публикации вакансии или None, если дата отсутствует.
        """
        pass
