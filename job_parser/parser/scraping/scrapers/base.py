import abc
import datetime
from dataclasses import asdict, dataclass
from typing import AsyncGenerator

from bs4 import BeautifulSoup


@dataclass
class Vacancy:
    job_board: str
    url: str
    title: str
    city: str
    description: str
    salary_from: int | None
    salary_to: int | None
    salary_currency: str | None
    company: str
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

    def __init__(self, job_board: str) -> None:
        self.job_board = job_board

    async def get_vacancy_details(
        self, page: tuple[str, str]
    ) -> AsyncGenerator[dict, None]:
        """Извлекает информацию о вакансии со страницы вакансии.

        Метод принимает кортеж из двух элементов: HTML-кода страницы и URL-адреса.
        Затем он создает объект BeautifulSoup из HTML-кода и использует абстрактные
        методы для извлечения информации о вакансии. Полученная информация сохраняется
        в экземпляре класса Vacancy и возвращается как результат генератора.

        Args:
            page (tuple[str, str]): Кортеж из двух элементов: HTML-кода страницы 
            и URL-адреса.

        Yields:
            AsyncGenerator[dict, None]: Словарь с информацией о вакансии.

        """
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

        yield asdict(vacancy)

    @abc.abstractmethod
    async def get_title(self, soup: BeautifulSoup) -> str:
        """Извлекает название вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_description(self, soup: BeautifulSoup) -> str:
        """Извлекает описание вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Описание вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_city(self, soup: BeautifulSoup) -> str:
        """Извлекает город вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Город вакансии.
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
    async def get_company(self, soup: BeautifulSoup) -> str:
        """Извлекает название компании со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название компании.
        """
        pass

    @abc.abstractmethod
    async def get_experience(self, soup: BeautifulSoup) -> str | None:
        """Извлекает требуемый опыт работы со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Требуемый опыт работы.
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

        Returns:
            bool: True, если вакансия удаленная, иначе False.
        """
        pass

    @abc.abstractmethod
    async def get_published_at(self, soup: BeautifulSoup) -> datetime.date | None:
        """Извлекает дату публикации вакансии со страницы вакансии.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            публикации не указана.
        """
        pass
