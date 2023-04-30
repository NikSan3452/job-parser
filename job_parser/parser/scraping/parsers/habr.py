import asyncio
import datetime
import re
from typing import AsyncGenerator

from bs4 import BeautifulSoup
from logger import logger, setup_logging
from parser.scraping.fetching import Fetcher

setup_logging()


class HabrParser:
    """Класс описывает методы парсинга сайта Habr career"""

    def __init__(self, fetcher: Fetcher) -> None:
        self.fetcher = fetcher

    async def get_vacancy_details(self, page: tuple) -> AsyncGenerator:
        """Получает детали вакансии.

        Args:
            page (tuple): html страница.

        Returns:
            AsyncGenerator: Асинхронный генератор с вакансиями.

        Yields:
            Iterator[AsyncGenerator]: Вакансия.
        """
        vacancy: dict = {}

        html, url = page
        soup = BeautifulSoup(html, "lxml")
        vacancy["job_board"] = "Habr career"
        vacancy["url"] = url

        (
            vacancy["title"],
            vacancy["city"],
            vacancy["description"],
            vacancy["salary"],
            vacancy["company"],
            vacancy["experience"],
            vacancy["type_of_work"],
            vacancy["remote"],
            vacancy["published_at"],
        ) = await asyncio.gather(
            self.__get_title(soup),
            self.__get_city(soup),
            self.__get_description(soup),
            self.__get_salary(soup),
            self.__get_company(soup),
            self.__get_experience(soup),
            self.__get_type_of_work(soup),
            self.__get_remote(soup),
            self.__get_published_at(soup),
        )

        logger.debug(
            f"Идет получение деталей вакансии со страницы {vacancy.get('url')}"
        )
        yield vacancy

    async def __get_title(self, soup: BeautifulSoup) -> str:
        """Получает заголовок вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Заголовок.
        """
        title = "Не указано"
        h1 = soup.find("h1", class_="page-title__title")
        if h1:
            title = h1.text.strip().lower()
        return title

    async def __get_description(self, soup: BeautifulSoup) -> str:
        """Получает описание вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Описание.
        """
        description = "Не указано"
        vacancy_description = soup.find("div", class_="vacancy-description__text")
        if vacancy_description:
            description = vacancy_description.text.strip().lower()
        return description

    async def __get_city(self, soup: BeautifulSoup) -> str:
        """Получает город вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Город.
        """
        city = "Не указано"

        location = soup.find(
            "a", href=lambda href: href and "/vacancies?city_id=" in href
        )
        if location:
            city = location.text.strip().lower()
        return city

    async def __get_salary(self, soup: BeautifulSoup) -> str:
        """Получает зарплату вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Зарплата.
        """
        salary = "Не указано"
        vacancy_salary = soup.find(
            "div", class_="basic-salary basic-salary--appearance-vacancy-header"
        )
        if vacancy_salary:
            salary = vacancy_salary.text.strip().lower()
        return salary

    async def __get_company(self, soup: BeautifulSoup) -> str:
        """Получает компанию вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Компания.
        """
        company = "Не указано"
        company_name = soup.find("div", class_="company_name")
        if company_name:
            company = company_name.find("a").text.strip().lower()
        return company

    async def __get_experience(self, soup: BeautifulSoup) -> str:
        """Получает требуемый опыт вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Опыт.
        """
        experience = "Не указано"
        text = ""
        exp = soup.find("a", href=lambda x: x and "/vacancies?qid=" in x)
        if exp:
            text = exp.text.strip()

        match text.lower():
            case "стажёр (intern)":
                experience = "Без опыта"
            case None:
                experience = "Без опыта"
            case "":
                experience = "Без опыта"
            case "младший (junior)":
                experience = "от 1 до 3 лет"
            case "средний (middle)":
                experience = "от 3 до 6 лет"
            case "старший (senior)" | "ведущий (lead)":
                experience = "от 6 лет"

        return experience

    async def __get_type_of_work(self, soup: BeautifulSoup) -> str:
        """Получает тип занятости вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            str: Тип занятости.
        """
        type_of_work = "Не указано"

        jobformat = soup.find_all(
            text=re.compile(
                r"Полный рабочий день|Неполный рабочий день|Можно удал[её]нно"
            )
        )
        if jobformat:
            jobformat = [string.text.strip().lower() for string in jobformat]
            if "" in jobformat:
                jobformat.remove("")
            type_of_work = ", ".join(jobformat)

        return type_of_work

    async def __get_remote(self, soup: BeautifulSoup) -> bool:
        """Определяет является ли вакансия удаленной.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            bool: True/False
        """
        remote_list = (
            "можно удалённо",
            "можно удаленно",
        )
        remote = False
        type_of_work = await self.__get_type_of_work(soup)
        for string in type_of_work.split(", "):
            for rem in remote_list:
                if string == rem:
                    remote = True

        return remote

    async def __get_published_at(self, soup: BeautifulSoup) -> datetime.date | None:
        """Получает дату публикации вакансии.

        Args:
            soup (BeautifulSoup): Экземпляр BeautifulSoup.

        Returns:
            datetime.date | None: Дата публикации.
        """
        published_at = None
        time_element = soup.find("time")
        if time_element:
            datetime_object = datetime.datetime.strptime(
                time_element["datetime"], "%Y-%m-%dT%H:%M:%S%z"
            )
            published_at = datetime_object.date()
        return published_at
