import datetime
import re
from parser.scraping.scrapers.base import Scraper
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from parser.scraping.configuration import Config

from bs4 import BeautifulSoup
from logger import setup_logging

setup_logging()


class HabrScraper(Scraper):
    """Класс HabrScraper предназначен для извлечения информации о вакансиях с сайта
    career.habr.com. Наследуется от базового класса Scraper.
    """

    def __init__(self, config: "Config") -> None:
        self.config = config
        self.selector = "vacancy-card__title-link"
        super().__init__(config, "habr")

    async def scrape(
        self, selector: str | None = None, domain: str | None = None
    ) -> None:
        """
        Асинхронный метод для сбора данных о вакансиях с указанной площадки.

        Args:
            selector (str | None): HTML - класс.
            domain: (str | None): Домен сайта.

        Returns: None
        """
        return await super().scrape(self.config.habr_domain, self.selector)

    async def get_title(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns str | None: Название вакансии.

        """
        title = None
        h1 = soup.find("h1", class_="page-title__title")
        if h1:
            title = h1.text.strip()
        return title

    async def get_description(self, soup: BeautifulSoup) -> str | None:
        """Извлекает описание вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): Описание вакансии.

        """
        description = None
        vacancy_description = soup.find("div", class_="vacancy-description__text")
        if vacancy_description:
            description = vacancy_description.prettify()
        return description

    async def get_city(self, soup: BeautifulSoup) -> str | None:
        """Извлекает город вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): Город вакансии.

        """
        city = None

        location = soup.find(
            "a", href=lambda href: href and "/vacancies?city_id=" in href
        )
        if location:
            city = location.text.strip()
        return city

    async def get_salary_from(self, soup: BeautifulSoup) -> int | None:
        """Извлекает минимальную зарплату из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (int | None): Минимальная зарплата или None, если
        информация отсутствует.

        """
        vacancy_salary = soup.find(
            "div", class_="basic-salary basic-salary--appearance-vacancy-header"
        )
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

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (int | None): Максимальная зарплата или None, если
        информация отсутствует.

        """
        vacancy_salary = soup.find(
            "div", class_="basic-salary basic-salary--appearance-vacancy-header"
        )
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

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): Символ валюты или None, если информация отсутствует.

        """
        vacancy_salary = soup.find(
            "div", class_="basic-salary basic-salary--appearance-vacancy-header"
        )
        currency = None

        if vacancy_salary:
            salary = vacancy_salary.text.strip()
            for symbol in ["₽", "€", "$", "₴", "₸"]:
                if symbol in salary:
                    currency = symbol
                    currency = self.config.utils.convert_currency(currency)
                    break
        return currency

    async def get_company(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название компании из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): Название компании.

        """
        company = "Не указано"
        company_name = soup.find("div", class_="company_name")
        if company_name:
            company = company_name.find("a").text.strip()
        return company

    async def get_experience(self, soup: BeautifulSoup) -> str | None:
        """Извлекает требуемый опыт работы из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): Требуемый опыт работы.

        """
        experience = "Не указано"
        text = ""
        exp = soup.find("a", href=lambda x: x and "/vacancies?qid=" in x)
        if exp:
            text = exp.text.strip()

        match text.lower():
            case "стажёр (intern)":
                experience = "Нет опыта"
            case None:
                experience = "Нет опыта"
            case "":
                experience = "Нет опыта"
            case "младший (junior)":
                experience = "От 1 года до 3 лет"
            case "средний (middle)":
                experience = "От 3 до 6 лет"
            case "старший (senior)" | "ведущий (lead)":
                experience = "От 6 лет"

        return experience

    async def get_schedule(self, soup: BeautifulSoup) -> str | None:
        """Извлекает график работы из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (str | None): График работы.

        """
        self.schedule = "Не указано"

        jobformat = soup.find_all(
            text=re.compile(
                r"Полный рабочий день|Неполный рабочий день|Можно удал[её]нно"
            )
        )
        if jobformat:
            jobformat = [string.text.strip() for string in jobformat]
            if "" in jobformat:
                jobformat.remove("")
            self.schedule = ", ".join(jobformat)
        return self.schedule

    async def get_remote(self) -> bool:
        """Определяет, является ли вакансия удаленной.

        Returns (bool): True, если вакансия является удаленной, иначе False.

        """
        if self.schedule:
            if re.search(r"Можно удал[её]нно", self.schedule):
                return True
        return False

    async def get_published_at(self, soup: BeautifulSoup) -> datetime.datetime | None:
        """Извлекает дату публикации вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns (datetime.datetime | None): Дата публикации вакансии или None,
        если информация отсутствует.

        """
        published_at = None
        time_element = soup.find("time")
        if time_element:
            published_at = datetime.datetime.strptime(
                time_element["datetime"], "%Y-%m-%dT%H:%M:%S%z"
            )
        return published_at
