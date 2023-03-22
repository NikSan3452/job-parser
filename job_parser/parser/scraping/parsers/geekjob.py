import asyncio
import datetime
from typing import AsyncGenerator
from bs4 import BeautifulSoup
from logger import setup_logging, logger
from parser.scraping.fetching import Fetcher

setup_logging()


class GeekjobParser:
    """Класс описывает методы парсинга сайта Geekjob"""

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
        vacancy["job_board"] = "Geekjob"
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
            self.get_title(soup),
            self.get_city(soup),
            self.get_description(soup),
            self.get_salary(soup),
            self.get_company(soup),
            self.get_experience(soup),
            self.get_type_of_work(soup),
            self.get_remote(soup),
            self.get_published_at(soup),
        )

        logger.debug(
            f"Идет получение деталей вакансии со страницы {vacancy.get('url')}"
        )
        yield vacancy

    async def get_title(self, soup: BeautifulSoup) -> str:
        """Получает заголовок вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Заголовок.
        """
        title = "Не указано"
        h1 = soup.find("h1")
        if h1:
            title = h1.text.strip().lower()
        return title

    async def get_city(self, soup: BeautifulSoup) -> str:
        """Получает город вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Город.
        """
        city = "Не указано"
        location = soup.find("div", class_="location")
        if location:
            city = location.text.strip().lower()
        return city

    async def get_description(self, soup: BeautifulSoup) -> str:
        """Получает описание вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Описание.
        """
        description = "Не указано"
        vacancy_description = soup.find(id="vacancy-description")
        if vacancy_description:
            description = vacancy_description.text.strip().lower()
        return description

    async def get_salary(self, soup: BeautifulSoup) -> str:
        """Получает зарплату вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Зарплата.
        """
        salary = "Не указано"
        vacancy_salary = soup.find("span", class_="salary")
        if vacancy_salary:
            salary = vacancy_salary.text.strip().lower()
        return salary

    async def get_company(self, soup: BeautifulSoup) -> str:
        """Получает компанию вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Компания.
        """
        company = "Не указано"
        company_name = soup.find("h5", class_="company-name")
        if company_name:
            company = company_name.find("a").text.strip().lower()
        return company

    async def get_experience(self, soup: BeautifulSoup) -> str:
        """Получает требуемый опыт вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Опыт.
        """
        experience = "Не указано"
        text = ""
        jobformat = soup.find("span", {"class": "jobformat"})
        if jobformat:
            text = jobformat.text.strip().split("\n")[-1]

        match text.lower():
            case "опыт работы менее 1 года":
                experience = "Без опыта"
            case "опыт работы любой":
                experience = "Без опыта"
            case None:
                experience = "Без опыта"
            case "":
                experience = "Без опыта"
            case "опыт работы от 1 года до 3х лет":
                experience = "от 1 до 3 лет"
            case "опыт работы от 3 до 5 лет":
                experience = "от 3 до 6 лет"
            case "опыт работы более 5 лет":
                experience = "от 6 лет"

        return experience

    async def get_type_of_work(self, soup: BeautifulSoup) -> str:
        """Получает тип занятости вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            str: Тип занятости.
        """
        type_of_work = "Не указано"
        string_list = []

        jobformat = soup.find("span", {"class": "jobformat"})
        if jobformat:
            text = jobformat.text.strip().lower().split("\n")
            for string in text:
                if string != text[-1]:
                    string_list.append(string)
            type_of_work = " ".join(string_list)
        return type_of_work

    async def get_remote(self, soup: BeautifulSoup) -> bool:
        """Определяет является ли вакансия удаленной.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            bool: True/False
        """
        remote = False
        type_of_work = await self.get_type_of_work(soup)
        if "удаленная" in type_of_work:
            remote = True
        return remote

    async def get_published_at(self, soup: BeautifulSoup) -> datetime.date | None:
        """Получает дату публикации вакансии.

        Args:
            soup (BeautifulSoup): Эксземпляр BeautifulSoup.

        Returns:
            datetime.date | None: Дата публикации.
        """
        published_at = None
        date = soup.find("div", class_="time")
        if date:
            published_at = await self.convert_date(date.text)
        return published_at

    async def convert_date(self, date: str) -> datetime.date:
        """Конвертирует полученное значение даты.

        Args:
            date (str): Дата.

        Returns:
            datetime.date: Дата в виде объекта datetime.
        """
        months = {
            "января": "January",
            "февраля": "February",
            "марта": "March",
            "апреля": "April",
            "мая": "May",
            "июня": "June",
            "июля": "July",
            "августа": "August",
            "сентября": "September",
            "октября": "October",
            "ноября": "November",
            "декабря": "December",
        }
        ru_date_str = date.strip().lower().split()
        if ru_date_str[1] in months:
            if len(ru_date_str) >= 3:
                en_date_str = (
                    f"{ru_date_str[0]} {months[ru_date_str[1]]} {ru_date_str[2]}"
                )
            else:
                en_date_str = f"{ru_date_str[0]} {months[ru_date_str[1]]} {datetime.datetime.today().year}"

        date_obj = datetime.datetime.strptime(en_date_str, "%d %B %Y").date()

        return date_obj
