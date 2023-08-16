import abc
import datetime
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parser.parsing.config import ParserConfig

from logger import logger, setup_logging

# Логирование
setup_logging()


@dataclass
class Vacancy:
    job_board: str
    url: str | None
    title: str | None
    salary_from: int | None
    salary_to: int | None
    salary_currency: str | None
    city: str | None
    company: str | None
    employment: str | None
    experience: str | None
    published_at: datetime.date | None
    description: str = ""
    schedule: str | None = ""
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

    def __init__(self, config: "ParserConfig", parser: str) -> None:
        self.config = config
        self.parser = parser

        self.job_board = getattr(config, f"{parser}_job_board")
        self.fetcher = getattr(config, f"{parser}_fetcher")

    async def parse(self) -> None:
        """
        Асинхронный метод для парсинга вакансий.

        Получает список вакансий с помощью метода `get_vacancies`,
        затем для каждой вакансии из списка создает объект `Vacancy` с
        деталями конкретной вакансии. Далее вызывается метод `update_vacancy_data`,
        в котором реализуется получение дополнительных деталей вакансии.
        Сформированные объект добавляются в список `parsed_vacancy_list`,
        а затем при помощи метода `record` записываются в базу данных .
        В конце работы метода выводится сообщение о завершении сбора вакансий
        с указанием источника и количества собранных вакансий.

        Returns: None
        """
        vacancy_list: list[dict] = await self.fetcher.get_vacancies()
        parsed_vacancy_list: list[Vacancy] = []
        vacancy_data: Vacancy | None = None
        vacancy_count: int = 0

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
                published_at=await self.get_published_at(vacancy),
            )

            updated_vacancy_data = await self.update_vacancy_data(vacancy, vacancy_data)
            parsed_vacancy_list.append(updated_vacancy_data)
            vacancy_count += 1

        await self.config.db.record(parsed_vacancy_list)

        logger.debug(
            f"Сбор вакансий с {self.job_board} завершен. Собрано вакансий: {vacancy_count}"
        )

        return None

    async def update_vacancy_data(
        self, vacancy: dict, vacancy_data: Vacancy
    ) -> Vacancy:
        """
        Асинхронный метод для обновления данных о вакансии.

        Метод принимает на вход словарь `vacancy` и объект `Vacancy` с данными
        о вакансии. В зависимости от значения атрибута `job_board`, метод обновляет
        данные разными способами, а также устанавливает необходимый интервал
        между запросами. Полученные результаты сохраняются в соответствующие
        атрибуты объекта `Vacancy`.

        Args:
            vacancy (dict): Словарь с данными о вакансии.
            vacancy_data (Vacancy): Объект с данными о вакансии.

        Returns:
            vacancy_data (Vacancy) Обновленные данные вакансии.
        """
        updated_vacancy_data = copy(vacancy_data)
        if self.job_board == "HeadHunter":
            details = await self.fetcher.get_vacancy_details(vacancy)
            description = await self.get_description(details)
            schedule = await self.get_schedule(details)
            remote = await self.get_remote(schedule)

            updated_vacancy_data.description = description
            updated_vacancy_data.schedule = schedule
            updated_vacancy_data.remote = remote

        if self.job_board == "Zarplata":
            details = await self.fetcher.get_vacancy_details(vacancy)
            description = await self.get_description(details)
            schedule = await self.get_schedule(details)
            remote = await self.get_remote(schedule)

            updated_vacancy_data.description = description
            updated_vacancy_data.schedule = schedule
            updated_vacancy_data.remote = remote

        if self.job_board == "SuperJob":
            updated_vacancy_data.description = await self.get_description(vacancy)
            updated_vacancy_data.schedule = await self.get_schedule(vacancy)
            updated_vacancy_data.remote = await self.get_remote(vacancy_data.employment)

        if self.job_board == "Trudvsem":
            updated_vacancy_data.description = await self.get_description(vacancy)
            updated_vacancy_data.schedule = await self.get_schedule(vacancy)
            updated_vacancy_data.remote = await self.get_remote(vacancy_data.schedule)

        return updated_vacancy_data

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
    async def get_salary_from(self, vacancy: dict) -> int | None:
        """
        Абстрактный асинхронный метод для получения минимальной зарплаты.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_to(self, vacancy: dict) -> int | None:
        """
        Абстрактный асинхронный метод для получения максимальной зарплаты.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Максимальная зарплата по вакансии или None, если зарплата
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
    async def get_remote(self, schedule: str | None) -> bool:
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
    async def get_published_at(self, vacancy: dict) -> datetime.datetime | None:
        """
        Абстрактный асинхронный метод для получения даты публикации вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.datetime | None: Дата публикации вакансии или None, если 
            дата отсутствует.
        """
        pass
