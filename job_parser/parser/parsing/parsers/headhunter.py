import datetime
import re

from logger import setup_logging

from ..config import ParserConfig
from ..utils import Utils
from .base import Parser

# Логирование
setup_logging()

utils = Utils()


class Headhunter(Parser):
    """
    Класс для парсинга вакансий с сайта HeadHunter.

    Наследуется от класса Parser.
    Класс Headhunter предназначен для парсинга вакансий с сайта HeadHunter.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта HeadHunter.
    """

    def __init__(self, config: ParserConfig, parser: str = "hh") -> None:
        super().__init__(config, parser)

    async def parsing_vacancy_headhunter(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта HeadHunter.

        Метод вызывает метод vacancy_parsing родительского класса Parser
        с параметрами запроса.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        return await super().vacancy_parsing()

    async def get_url(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод возвращает значение ключа "alternate_url" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        return vacancy.get("alternate_url", None)

    async def get_title(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод возвращает значение ключа "name" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        return vacancy.get("name", None)

    async def get_salary_from(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод получает значение ключа "salary" из словаря vacancy и возвращает значение
        ключа "from".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary = vacancy.get("salary", None)
        return salary.get("from", None) if salary else None

    async def get_salary_to(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод получает значение ключа "salary" из словаря vacancy и возвращает значение
        ключа "to".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary = vacancy.get("salary", None)
        return salary.get("to", None) if salary else None

    async def get_salary_currency(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод получает значение ключа "salary" из словаря vacancy и возвращает значение
        ключа "currency".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        salary = vacancy.get("salary", None)
        return salary.get("currency", None) if salary else None

    async def get_description(self, details: dict) -> str:
        """
        Асинхронный метод для получения описания вакансии.

        Метод принимает на вход словарь с деталями вакансии и возвращает строку
        с описанием вакансии. Метод получает значение ключа "description" из словаря
        с деталями вакансии. Если значение равно `None`, то метод возвращает
        строку "Нет описания". В противном случае метод возвращает полученное значение.

        Args:
            details (dict): Словарь с деталями вакансии.

        Returns:
            str: Строка с описанием вакансии.
        """
        description = details.get("description", None)
        return description if description else "Нет описания"

    async def get_city(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "area" из словаря vacancy и возвращает значение
        ключа "name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        area = vacancy.get("area", None)
        return area.get("name", None) if area else None

    async def get_company(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод получает значение ключа "employer" из словаря vacancy и возвращает
        значение ключа "name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        employer = vacancy.get("employer", None)
        return employer.get("name", None) if employer else None

    async def get_employment(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения типа занятости.

        Метод получает значение ключа "employment" из словаря vacancy и возвращает
        значение ключа "name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип занятости по вакансии или None, если тип занятости
            отсутствует.
        """
        employment = vacancy.get("employment", None)
        return employment.get("name", None) if employment else None

    async def get_schedule(self, details: dict) -> str | None:
        """
        Асинхронный метод для получения графика работы.

        Метод принимает на вход словарь с деталями вакансии и возвращает строку
        с графиком работы или `None`. Метод получает значение ключа "schedule" из
        словаря с деталями вакансии. Если значение равно `None`, то метод возвращает
        `None`. В противном случае метод получает значение ключа "name" из словаря
        со значением ключа "schedule" и вызывает метод `get_remote` с передачей ему
        полученного значения. Полученное значение возвращается как результат
        работы метода.

        Args:
            details (dict): Словарь с деталями вакансии.

        Returns:
            str | None: Строка с графиком работы или `None`.
        """
        schedule = details.get("schedule", None)
        schedule = schedule.get("name", None) if schedule else None
        await self.get_remote(schedule)
        return schedule

    async def get_remote(self, schedule: str) -> bool:
        """
        Асинхронный метод для определения удаленной работы.

        Метод принимает на вход строку с графиком работы и возвращает булево значение,
        указывающее на то, является ли работа удаленной. Метод проверяет, равно ли
        переданное значение `None`. Если это так, то метод возвращает `False`.
        В противном случае метод проверяет, содержит ли переданная строка необходимую
        подстроку с помощью функции `search` модуля `re`.
        Если подстрока найдена, то метод возвращает `True`, иначе - `False`.

        Args:
            schedule (str): Строка с графиком работы.

        Returns:
            bool: Булево значение, указывающее на то, является ли работа удаленной.
        """
        if schedule:
            if re.search(r"Удал[её]нн", schedule):
                return True
        return False

    async def get_experience(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения опыта работы.

        Метод получает значение ключа "experience" из словаря vacancy и возвращает
        значение ключа "name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Опыт работы по вакансии или None, если опыт работы отсутствует.
        """
        experience = vacancy.get("experience", None)
        return experience.get("name", None) if experience else None

    async def get_published_at(self, vacancy: dict) -> datetime.date | None:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Метод получает значение ключа "published_at" из словаря vacancy и преобразует
        его в формат даты. Возвращает эту дату.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        date = vacancy.get("published_at", None)
        return (
            datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S%z").date()
            if date
            else None
        )
