import datetime
import re
from typing import TYPE_CHECKING

from bs4 import BeautifulSoup
from logger import setup_logging

from parser.scraping.scrapers.base import Scraper

if TYPE_CHECKING:
    from parser.scraping.configuration import Config

setup_logging()


class GeekjobScraper(Scraper):
    """Класс GeekjobParser предназначен для извлечения информации о вакансиях
    с сайта geekjob.ru. Наследуется от базового класса Scraper.
    """

    def __init__(self, config: "Config") -> None:
        self.config = config
        self.selector = "title"
        super().__init__(config, "geekjob")

    async def scrape(self) -> None:
        """
        Асинхронный метод для сбора данных о вакансиях с указанной площадки.

        В этом методе вызывается родительский метод `scrape` с передачей ему аргументов
        в виде HTML-класса и домена сайта.

        Returns:
            None
        """
        return await super().scrape(self.selector, self.config.geekjob_domain)

    async def get_title(self, soup: BeautifulSoup) -> str:
        """Извлекает название вакансии из объекта BeautifulSoup.

        Ищет тег `h1` на странице и возвращает его текстовое содержимое.
        Если тег не найден, возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название вакансии.

        """
        title = "Не указано"
        h1 = soup.find("h1")
        if h1:
            title = h1.text.strip()
        return title

    async def get_city(self, soup: BeautifulSoup) -> str:
        """Извлекает город вакансии из объекта BeautifulSoup.

        Ищет тег `div` с классом `location` на странице и возвращает его
        текстовое содержимое. Если тег не найден, возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Город вакансии.

        """
        city = "Не указано"
        location = soup.find("div", class_="location")
        if location:
            city = location.text.strip()
        return city

    async def get_description(self, soup: BeautifulSoup) -> str:
        """Извлекает описание вакансии из объекта BeautifulSoup.

        Ищет элемент с идентификатором `vacancy-description` на странице и возвращает
        его HTML-код. Если элемент не найден, возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Описание вакансии.

        """
        description = "Не указано"
        vacancy_description = soup.find(id="vacancy-description")
        if vacancy_description:
            description = vacancy_description.prettify()
        return description

    async def get_salary_from(self, soup: BeautifulSoup) -> int | None:
        """Извлекает минимальную зарплату из объекта BeautifulSoup.

        Ищет тег `span` с классом `salary` на странице и извлекает из его текстового
        содержимого минимальную зарплату с помощью регулярного выражения. Если тег не
        найден или информация о зарплате отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Минимальная зарплата или None, если информация отсутствует.

        """
        vacancy_salary = soup.find("span", class_="salary")
        salary_from: int | None = None

        if vacancy_salary:
            salary = vacancy_salary.text.strip()
            salary = salary.replace(" ", "")
            match = re.search(r"от(\d+)", salary)
            if match:
                salary_from = int(match.group(1))
        return int(salary_from) if salary_from else None

    async def get_salary_to(self, soup: BeautifulSoup) -> int | None:
        """Извлекает максимальную зарплату из объекта BeautifulSoup.

        Ищет тег `span` с классом `salary` на странице и извлекает из его
        текстового содержимого максимальную зарплату с помощью регулярного выражения.
        Если тег не найден или информация о зарплате отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Максимальная зарплата или None, если информация отсутствует.

        """
        vacancy_salary = soup.find("span", class_="salary")
        salary_to: int | None = None

        if vacancy_salary:
            salary = vacancy_salary.text.strip()
            salary = salary.replace(" ", "")
            match = re.search(r"до(\d+)", salary)
            if match:
                salary_to = int(match.group(1))
        return int(salary_to) if salary_to else None

    async def get_salary_currency(self, soup: BeautifulSoup) -> str | None:
        """Извлекает валюту зарплаты из объекта BeautifulSoup.

        Ищет тег `span` с классом `salary` на странице и извлекает из его текстового
        содержимого символ валюты. Если тег не найден или информация о зарплате
        отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Символ валюты или None, если информация отсутствует.

        """
        vacancy_salary = soup.find("span", class_="salary")
        currency = None

        if vacancy_salary:
            salary = vacancy_salary.text.strip()
            for symbol in ["₽", "€", "$", "₴", "₸"]:
                if symbol in salary:
                    currency = symbol
                    currency = self.config.utils.convert_currency(currency)
                    break

        return currency

    async def get_company(self, soup: BeautifulSoup) -> str:
        """Извлекает название компании из объекта BeautifulSoup.

        Ищет тег `h5` с классом `company-name` на странице и возвращает текстовое
        содержимое его дочернего тега `a`. Если тег не найден, возвращает строку
        "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название компании.

        """
        company = "Не указано"
        company_name = soup.find("h5", class_="company-name")
        if company_name:
            company = company_name.find("a").text.strip()
        return company

    async def get_experience(self, soup: BeautifulSoup) -> str | None:
        """Извлекает требуемый опыт работы из объекта BeautifulSoup.

        Ищет тег `span` с классом `jobformat` на странице и анализирует его текстовое
        содержимое. В зависимости от текста возвращает строку с требуемым опытом работы.
        Если тег не найден или информация отсутствует, возвращает строку "Нет опыта".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Требуемый опыт работы.

        """
        experience = None
        text = ""
        jobformat = soup.find("span", {"class": "jobformat"})
        if jobformat:
            text = jobformat.text.strip().split("\n")[-1]

        match text.lower():
            case "опыт работы менее 1 года":
                experience = "Нет опыта"
            case "опыт работы любой":
                experience = "Нет опыта"
            case None:
                experience = "Нет опыта"
            case "":
                experience = "Нет опыта"
            case "опыт работы от 1 года до 3х лет":
                experience = "От 1 года до 3 лет"
            case "опыт работы От 3 до 5 лет":
                experience = "От 3 до 6 лет"
            case "опыт работы более 5 лет":
                experience = "От 6 лет"

        return experience

    async def get_schedule(self, soup: BeautifulSoup) -> str | None:
        """Извлекает график работы из объекта BeautifulSoup.

        Ищет тег `span` с классом `jobformat` на странице и анализирует его текстовое
        содержимое. Возвращает строку с графиком работы. Если тег не найден или
        информация отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: График работы или None, если информация отсутствует.

        """
        self.schedule = None
        string_list: list[str] = []

        jobformat = soup.find("span", {"class": "jobformat"})
        if jobformat:
            text = jobformat.text.strip().split("\n")
            for string in text:
                if string != text[-1]:
                    string_list.append(string)
            self.schedule = " ".join(string_list)
        return self.schedule

    async def get_remote(self) -> bool:
        """Определяет, является ли вакансия удаленной.

        Анализирует строку с графиком работы, полученную методом get_schedule.
        Если в строке присутствует слово "Удаленная" или "Удаленно", возвращает True.
        В противном случае возвращает False.

        Returns:
            bool: True, если вакансия является удаленной, иначе False.

        """
        if self.schedule:
            if re.search(r"Удал[её]нн", self.schedule):
                return True
        return False

    async def get_published_at(self, soup: BeautifulSoup) -> datetime.date | None:
        """Извлекает дату публикации вакансии из объекта BeautifulSoup.

        Ищет тег `div` с классом `time` на странице и анализирует
        его текстовое содержимое. Преобразует текст в объект datetime.date и возвращает
        его. Если тег не найден или информация отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если информация
            отсутствует.

        """
        published_at = None
        date = soup.find("div", class_="time")
        if date:
            published_at = await self.convert_date(date.text)
        return published_at

    async def convert_date(self, date: str) -> datetime.datetime:
        """Конвертирует полученное значение даты.

        Args:
            date (str): Дата.

        Returns:
            datetime.datetime: Дата в виде объекта datetime.
        """
        months = {
            "января": 1,
            "февраля": 2,
            "марта": 3,
            "апреля": 4,
            "мая": 5,
            "июня": 6,
            "июля": 7,
            "августа": 8,
            "сентября": 9,
            "октября": 10,
            "ноября": 11,
            "декабря": 12,
        }
        ru_date_str = date.strip().lower().split()
        if ru_date_str[1] in months:
            if len(ru_date_str) >= 3:
                en_date_str = (
                    f"{ru_date_str[0]}-{months[ru_date_str[1]]:02d}-{ru_date_str[2]}"
                )
            else:
                en_date_str = f"{ru_date_str[0]}-{months[ru_date_str[1]]:02d}-{datetime.datetime.today().year}"

        en_date = datetime.datetime.strptime(en_date_str, "%d-%m-%Y")
        
        return en_date
