import abc
import datetime
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from parser.scraping.configuration import Config

from logger import logger, setup_logging

setup_logging()


@dataclass
class Vacancy:
    job_board: str
    url: str
    title: str | None
    city: str | None
    description: str | None
    salary_from: int | None
    salary_to: int | None
    salary_currency: str | None
    company: str | None
    experience: str | None
    schedule: str | None
    remote: bool
    published_at: datetime.date | None


class Scraper(abc.ABC):
    """Класс Scraper предназначен для извлечения информации о вакансиях с сайтов
    поиска работы.

    Args:
        job_board (str): Название сайта поиска работы.
    """

    def __init__(self, config: "Config", parser: str) -> None:
        self.config = config
        self.parser = parser

        self.job_board = getattr(config, f"{parser}_job_board")
        self.fetcher = getattr(config, f"{parser}_fetcher")

    async def scrape(self, selector: str, domain: str) -> None:
        """
        Асинхронный метод для сбора данных о вакансиях с указанной площадки.

        Сначала вызывается метод `get_vacancy_links` для получения
        списка ссылок на вакансии с указанного домена. Затем вызывается метод
        `fetch_vacancy_pages` для получения страниц вакансий.

        Далее создается объект `BeautifulSoup` для парсинга HTML-кода страницы.
        Затем вызываются различные методы для извлечения информации с использованием
        объекта `BeautifulSoup`. Эта информация используется для создания объекта
        `Vacancy`, который затем добавляется в список обработанных вакансий.

        В конце метода список обработанных вакансий записывается в базу данных
        с помощью метода `record`.

        Args:
            selector (str): Название html-класса, по которому будет осуществлен поиск.
            domain (str): Домен сайта площадки.
        Returns:
            None
        """
        parsed_vacancy_list: list[dict] = []
        links: list[str] = await self.fetcher.get_vacancy_links(selector, domain)
        vacancy_list: list[dict] = await self.fetcher.fetch_vacancy_pages(links)
        vacancy_count: int = 0

        for page in vacancy_list:
            html, url = page
            soup = BeautifulSoup(html, "lxml")
            vacancy = Vacancy(
                job_board=self.job_board,
                url=url,
                title=await self.get_title(soup),
                city=await self.get_city(soup),
                description=await self.get_description(soup),
                salary_from=await self.get_salary_from(soup),
                salary_to=await self.get_salary_to(soup),
                salary_currency=await self.get_salary_currency(soup),
                company=await self.get_company(soup),
                experience=await self.get_experience(soup),
                schedule=await self.get_schedule(soup),
                remote=await self.get_remote(),
                published_at=await self.get_published_at(soup),
            )
            parsed_vacancy_list.append(asdict(vacancy))
            vacancy_count += 1

        logger.debug(
            f"Сбор вакансий с площадки {self.job_board} завершен. Собрано вакансий: {vacancy_count}"
        )
        await self.config.db.record(parsed_vacancy_list)

    @abc.abstractmethod
    async def get_title(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Название вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_description(self, soup: BeautifulSoup) -> str | None:
        """Извлекает описание вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Описание вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_city(self, soup: BeautifulSoup) -> str | None:
        """Извлекает город вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Город вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_salary_from(self, soup: BeautifulSoup) -> int | None:
        """Извлекает минимальную зарплату со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Минимальная зарплата или None, если зарплата не указана.
        """
        pass

    @abc.abstractmethod
    async def get_salary_to(self, soup: BeautifulSoup) -> int | None:
        """Извлекает максимальную зарплату со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Максимальная зарплата или None, если зарплата не указана.
        """
        pass

    @abc.abstractmethod
    async def get_salary_currency(self, soup: BeautifulSoup) -> str | None:
        """Извлекает валюту зарплаты со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Валюта зарплаты или None, если зарплата не указана.
        """
        pass

    @abc.abstractmethod
    async def get_company(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название компании со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Название компании.
        """
        pass

    @abc.abstractmethod
    async def get_experience(self, soup: BeautifulSoup) -> str | None:
        """Извлекает требуемый опыт работы со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Требуемый опыт работы.
        """
        pass

    @abc.abstractmethod
    async def get_schedule(self, soup: BeautifulSoup) -> str | None:
        """Извлекает график работы со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: График работы или None, если график работы не указан.
        """
        pass

    @abc.abstractmethod
    async def get_remote(self) -> bool:
        """Определяет, является ли вакансия удаленной.

        Returns (bool): True, если вакансия удаленная, иначе False.
        """
        pass

    @abc.abstractmethod
    async def get_published_at(self, soup: BeautifulSoup) -> datetime.datetime | None:
        """Извлекает дату публикации вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            datetime.datetime | None: Дата публикации вакансии или None, если дата
            публикации не указана.
        """
        pass
