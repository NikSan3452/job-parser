import datetime
import locale
import re
from typing import TYPE_CHECKING

from django.utils import timezone

from parser.scraping.scrapers.base import Scraper

if TYPE_CHECKING:
    from parser.scraping.configuration import Config

from bs4 import BeautifulSoup
from logger import setup_logging

setup_logging()


class CareeristScraper(Scraper):
    """Класс JobfilterScraper предназначен для извлечения информации о вакансиях с сайта
    jobfilter.ru. Наследуется от базового класса Scraper.
    """

    def __init__(self, config: "Config") -> None:
        self.config = config
        self.selector = "vak_hl_ vacancyLink"
        super().__init__(config, "careerist")

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
        return await super().scrape(self.config.careerist_domain, self.selector)

    async def get_title(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): Название вакансии.

        """
        title = None
        h1 = soup.find("h1")
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
        vacancy_description = soup.find_all("div", class_="b-b-1")
        if len(vacancy_description) > 2:
            vacancy_description = vacancy_description[2]
            if vacancy_description:
                description = vacancy_description.prettify()
        return description

    async def get_city(self, soup: BeautifulSoup) -> str | None:
        """Извлекает город вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): Город вакансии.

        """
        city = None

        city_p = soup.find("p", text="Город:")
        city = city_p.find_next_sibling("p").text.strip() if city_p else None
        return city

    async def get_salary_from(self, soup: BeautifulSoup) -> int | None:
        """Извлекает минимальную зарплату из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (int | None): Минимальная зарплата или None, если
        информация отсутствует.

        """
        salary_p = soup.find("p", class_="h5")
        salary_text = salary_p.text if salary_p else None
        salary_numbers = re.findall(r"\d+", salary_text) if salary_text else None
        salary_from = (
            int("".join(salary_numbers[:2]))
            if salary_numbers and salary_numbers[:2]
            else None
        )
        return salary_from

    async def get_salary_to(self, soup: BeautifulSoup) -> int | None:
        """Извлекает максимальную зарплату из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (int | None): Максимальная зарплата или None, если
        информация отсутствует.

        """
        salary_p = soup.find("p", class_="h5")
        salary_text = salary_p.text if salary_p else None
        salary_numbers = re.findall(r"\d+", salary_text) if salary_text else None
        salary_to = (
            int("".join(salary_numbers[2:]))
            if salary_numbers and salary_numbers[2:]
            else None
        )
        return salary_to

    async def get_salary_currency(self, soup: BeautifulSoup) -> str | None:
        """Извлекает валюту зарплаты из объекта BeautifulSoup.

        Args:
        soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): Символ валюты или None, если информация отсутствует.

        """
        salary_p = soup.find("p", class_="h5")
        salary_text = salary_p.text if salary_p else None
        currency = salary_text.split()[-1] if salary_text else None
        return currency

    async def get_company(self, soup: BeautifulSoup) -> str | None:
        """Извлекает название компании из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): Название компании.

        """
        company = None
        company_a = soup.find("a", href=re.compile(r"careerist.ru/companies"))
        company = company_a.text.strip() if company_a else None
        return company

    async def get_experience(self, soup: BeautifulSoup) -> str | None:
        """Извлекает требуемый опыт работы из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): Требуемый опыт работы.

        """
        experience = None
        experience_p = soup.find("p", text="Опыт:")
        experience = (
            experience_p.find_next_sibling("p").text.strip() if experience_p else None
        )

        match experience if experience else None:
            case "Нет опыта":
                experience = "Нет опыта"
            case "Менее года":
                experience = "Нет опыта"
            case None:
                experience = "Нет опыта"
            case "":
                experience = "Нет опыта"
            case "Более 1 года":
                experience = "От 1 года до 3 лет"
            case "Более 2 лет":
                experience = "От 1 года до 3 лет"
            case "Более 3 лет":
                experience = "От 3 до 6 лет"
            case "Более 6 лет":
                experience = "От 6 лет"

        return experience

    async def get_schedule(self, soup: BeautifulSoup) -> str | None:
        """Извлекает график работы из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns: (str | None): График работы.

        """
        self.schedule = None

        schedule_p = soup.find("p", text="Занятость:")
        self.schedule = (
            schedule_p.find_next_sibling("p").text.strip() if schedule_p else None
        )
        return self.schedule

    async def get_remote(self) -> bool:
        """Определяет, является ли вакансия удаленной.

        Returns: (bool): True, если вакансия является удаленной, иначе False.

        """
        if self.schedule:
            if re.search(r"Удал[её]нн", self.schedule):
                return True
        return False



    async def get_published_at(self, soup: BeautifulSoup) -> datetime.datetime | None:
        """Извлекает дату публикации вакансии из объекта BeautifulSoup.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            datetime.datetime | None: Дата публикации вакансии или None, если информация
            отсутствует.

        """
        published_at = None
        time_p = soup.find("p", class_="pull-xs-right m-l-1 text-small")
        time_text = time_p.text.strip() if time_p else None
        locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")
        naive_datetime = (
            datetime.datetime.strptime(time_text, "%d %B %Y") if time_text else None
        )
        if naive_datetime:
            now = timezone.now()
            published_at = timezone.make_aware(datetime.datetime(
                year=naive_datetime.year,
                month=naive_datetime.month,
                day=naive_datetime.day,
                hour=now.hour,
                minute=now.minute,
                second=now.second
            ))
        else:
            published_at = timezone.now()
        return published_at

