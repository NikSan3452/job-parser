import datetime
import re
from parser.scraping.configuration import Config
from parser.scraping.fetching import Fetcher
from parser.scraping.scrapers.base import Scraper

import aiohttp
from bs4 import BeautifulSoup
from logger import setup_logging

setup_logging()


class HabrParser(Scraper):
    """Класс HabrParser предназначен для извлечения информации о вакансиях с сайта 
    career.habr.com. Наследуется от базового класса Scraper. 

    Args:
        config (Config): Объект класса Config, содержит настройки для парсера.
        session (aiohttp.ClientSession): Объект сессии aiohttp.

    """

    def __init__(self, config: Config, session: aiohttp.ClientSession) -> None:
        self.job_board = config.habr_job_board
        self.config = config
        self.session = session
        self.fetcher = Fetcher(config.HABR_URL, config.HABR_PAGES_COUNT, self.session)
        super().__init__(self.fetcher, self.config, self.job_board)

    async def save_habr_data(self) -> int:
        """Сохраняет информацию о вакансиях с сайта career.habr.com в базе данных.

        Вызывает метод save_data базового класса Scraper.

        Returns:
            int: Количество сохраненных вакансий.

        """
        return await super().save_data()

    async def get_title(self, soup: BeautifulSoup) -> str:
        """Извлекает название вакансии из объекта BeautifulSoup.

        Ищет тег `h1` с классом `page-title__title` на странице и возвращает его 
        текстовое содержимое. Если тег не найден, возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название вакансии.

        """
        title = "Не указано"
        h1 = soup.find("h1", class_="page-title__title")
        if h1:
            title = h1.text.strip()
        return title

    async def get_description(self, soup: BeautifulSoup) -> str:
        """Извлекает описание вакансии из объекта BeautifulSoup.

        Ищет элемент с классом `vacancy-description__text` на странице и возвращает 
        его HTML-код. Если элемент не найден, возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Описание вакансии.

        """
        description = "Не указано"
        vacancy_description = soup.find("div", class_="vacancy-description__text")
        if vacancy_description:
            description = vacancy_description.prettify()
        return description

    async def get_city(self, soup: BeautifulSoup) -> str:
        """Извлекает город вакансии из объекта BeautifulSoup.

        Ищет тег `a` с атрибутом `href`, содержащим подстроку `/vacancies?city_id=` 
        на странице и возвращает его текстовое содержимое. Если тег не найден, 
        возвращает строку "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Город вакансии.

        """
        city = "Не указано"

        location = soup.find(
            "a", href=lambda href: href and "/vacancies?city_id=" in href
        )
        if location:
            city = location.text.strip()
        return city

    async def get_salary_from(self, soup: BeautifulSoup) -> int | None:
        """Извлекает минимальную зарплату из объекта BeautifulSoup.

        Ищет тег `div` с классом `basic-salary basic-salary--appearance-vacancy-header` 
        на странице и извлекает из его текстового содержимого минимальную зарплату с 
        помощью регулярного выражения. Если тег не найден или информация о зарплате 
        отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Минимальная зарплата или None, если информация отсутствует.

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

        Ищет тег `div` с классом `basic-salary basic-salary--appearance-vacancy-header` 
        на странице и извлекает из его текстового содержимого максимальную зарплату с 
        помощью регулярного выражения. Если тег не найден или информация о зарплате 
        отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            int | None: Максимальная зарплата или None, если информация отсутствует.

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

        Ищет тег `div` с классом `basic-salary basic-salary--appearance-vacancy-header` 
        на странице и извлекает из его текстового содержимого символ валюты. Если тег 
        не найден или информация о зарплате отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str | None: Символ валюты или None, если информация отсутствует.

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
                    break
        return currency

    async def get_company(self, soup: BeautifulSoup) -> str:
        """Извлекает название компании из объекта BeautifulSoup.

        Ищет тег `div` с классом `company_name` на странице и возвращает текстовое 
        содержимое его дочернего тега `a`. Если тег не найден, возвращает строку 
        "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Название компании.

        """
        company = "Не указано"
        company_name = soup.find("div", class_="company_name")
        if company_name:
            company = company_name.find("a").text.strip()
        return company

    async def get_experience(self, soup: BeautifulSoup) -> str:
        """Извлекает требуемый опыт работы из объекта BeautifulSoup.

        Ищет тег `a` с атрибутом `href`, содержащим подстроку `/vacancies?qid=` на 
        странице и анализирует его текстовое содержимое. В зависимости от текста 
        возвращает строку с требуемым опытом работы. Если тег не найден или информация 
        отсутствует, возвращает строку "Нет опыта".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: Требуемый опыт работы.

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

    async def get_schedule(self, soup: BeautifulSoup) -> str:
        """Извлекает график работы из объекта BeautifulSoup.

        Ищет все элементы текста на странице, содержащие подстроки 
        "Полный рабочий день", "Неполный рабочий день" или "Можно удаленно", и 
        объединяет их в строку с разделителем ", ". Возвращает полученную строку. 
        Если элементы не найдены или информация отсутствует, возвращает строку 
        "Не указано".

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            str: График работы.

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

        Анализирует строку с графиком работы, полученную методом get_schedule. 
        Если в строке присутствует подстрока "Можно удаленно", возвращает True. 
        В противном случае возвращает False.

        Returns:
            bool: True, если вакансия является удаленной, иначе False.

        """
        if self.schedule:
            if re.search(r"Можно удал[её]нно", self.schedule):
                return True
        return False


    async def get_published_at(self, soup: BeautifulSoup) -> datetime.date | None:
        """Извлекает дату публикации вакансии из объекта BeautifulSoup.

        Ищет тег `time` на странице и анализирует значение его атрибута `datetime`. 
        Преобразует значение атрибута в объект datetime.date и возвращает его. 
        Если тег не найден или информация отсутствует, возвращает None.

        Args:
            soup (BeautifulSoup): Объект BeautifulSoup со страницей вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если информация 
            отсутствует.

        """
        published_at = None
        time_element = soup.find("time")
        if time_element:
            datetime_object = datetime.datetime.strptime(
                time_element["datetime"], "%Y-%m-%dT%H:%M:%S%z"
            )
            published_at = datetime_object.date()
        return published_at
