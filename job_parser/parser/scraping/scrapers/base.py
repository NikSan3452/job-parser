import abc
import asyncio
import datetime
from parser.models import Vacancies
from parser.scraping.configuration import Config
from parser.scraping.fetching import Fetcher
from typing import AsyncGenerator

from bs4 import BeautifulSoup
from django.db import DatabaseError, Error, IntegrityError, ProgrammingError
from loguru import logger


class Scraper(abc.ABC):
    """Класс Scraper предназначен для извлечения информации о вакансиях с сайтов 
    поиска работы.

    Args:
        fetcher (Fetcher): Объект класса Fetcher, который используется для получения 
        данных с сайтов поиска работы.
        config (Config): Объект класса Config, который содержит настройки для парсера.
        job_board (str): Название сайта поиска работы.
    """
    def __init__(self, fetcher: Fetcher, config: Config, job_board: str) -> None:
        self.fetcher = fetcher
        self.config = config
        self.job_board = job_board

    async def get_vacancy_details(self, page: tuple) -> AsyncGenerator:
        """Извлекает информацию о вакансии со страницы вакансии.

        Метод принимает кортеж из двух элементов: HTML-кода страницы и URL-адреса. 
        Затем он создает объект BeautifulSoup из HTML-кода и использует абстрактные 
        методы для извлечения информации о вакансии. Полученная информация сохраняется 
        в словаре и возвращается как результат генератора.

        Args:
            page (tuple): Кортеж из двух элементов: HTML-кода страницы и URL-адреса.

        Yields:
            dict: Словарь с информацией о вакансии.

        """
        vacancy: dict = {}

        html, url = page
        soup = BeautifulSoup(html, "lxml")
        vacancy["job_board"] = self.job_board
        vacancy["url"] = url

        (
            vacancy["title"],
            vacancy["city"],
            vacancy["description"],
            vacancy["salary_from"],
            vacancy["salary_to"],
            vacancy["salary_currency"],
            vacancy["company"],
            vacancy["experience"],
            vacancy["schedule"],
            vacancy["remote"],
            vacancy["published_at"],
        ) = await asyncio.gather(
            self.get_title(soup),
            self.get_city(soup),
            self.get_description(soup),
            self.get_salary_from(soup),
            self.get_salary_to(soup),
            self.get_salary_currency(soup),
            self.get_company(soup),
            self.get_experience(soup),
            self.get_schedule(soup),
            self.get_remote(),
            self.get_published_at(soup),
        )
        yield vacancy

    async def save_data(self) -> int:
        """Сохраняет информацию о вакансиях в базе данных.

        Метод использует объект fetcher для получения ссылок на вакансии 
        и страниц вакансий. Затем он использует метод get_vacancy_details для 
        извлечения информации о вакансиях и сохраняет ее в базе данных с помощью 
        модели Vacancies. Возвращает количество сохраненных вакансий.

        Returns:
            int: Количество сохраненных вакансий.

        """
        links = await self.fetcher.fetch_vacancy_links(self.job_board)
        vacancy_counter = 0
        async for page in self.fetcher.fetch_vacancy_pages(links):
            async for vacancy in self.get_vacancy_details(page):
                try:
                    await Vacancies.objects.aget_or_create(**vacancy)
                except (Error, IntegrityError, DatabaseError, ProgrammingError) as exc:
                    logger.exception(exc)
                vacancy_counter += 1
        return vacancy_counter

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
    async def get_experience(self, soup: BeautifulSoup) -> str:
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
