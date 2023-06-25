import datetime
import re

from logger import setup_logging

from ..config import ParserConfig
from ..utils import Utils
from .base import Parser

# Логирование
setup_logging()

utils = Utils()


class SuperJob(Parser):
    """
    Класс для парсинга вакансий с сайта SuperJob.

    Наследуется от класса Parser.
    Класс SuperJob предназначен для парсинга вакансий с сайта SuperJob.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта SuperJob.
    """

    def __init__(self, config: ParserConfig) -> None:
        super().__init__(config, "sj")

    async def parsing_vacancy_superjob(self) -> dict:
        """
        Асинхронный метод для парсинга вакансий с сайта SuperJob.

        Метод вызывает метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        return await super().vacancy_parsing()

    async def get_url(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод возвращает значение ключа "link" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        return vacancy.get("link", None)

    async def get_title(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод возвращает значение ключа "profession" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        return vacancy.get("profession", None)

    async def get_salary_from(self, vacancy: dict) -> int | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод возвращает значение ключа "payment_from" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary_from = vacancy.get("payment_from", None)
        if int(salary_from) == 0:
            salary_from = None
        return int(salary_from) if salary_from else None

    async def get_salary_to(self, vacancy: dict) -> int | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод возвращает значение ключа "payment_to" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        salary_to = vacancy.get("payment_to", None)
        if int(salary_to) == 0:
            salary_to = None
        return int(salary_to) if salary_to else None

    async def get_salary_currency(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод возвращает значение ключа "currency" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        return vacancy.get("currency", None)

    async def get_description(self, vacancy: dict) -> str:
        """
        Асинхронный метод для получения описания вакансии.

        Метод принимает на вход словарь с данными о вакансии и возвращает строку
        с описанием вакансии. Метод получает значение ключа "vacancyRichText" из
        словаря с данными о вакансии. Если значение равно `None`, то метод возвращает
        строку "Нет описания". В противном случае метод возвращает полученное значение.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str: Строка с описанием вакансии.
        """
        return (
            vacancy.get("vacancyRichText", None)
            if vacancy.get("vacancyRichText", None)
            else "Нет описания"
        )

    async def get_city(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "town" из словаря vacancy и возвращает значение
        ключа "title".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        town = vacancy.get("town", None)
        return town.get("title", None) if town else None

    async def get_company(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод возвращает значение ключа "firm_name" из словаря vacancy.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        return vacancy.get("firm_name", None)

    async def get_employment(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения места работы.

        Метод принимает на вход словарь с данными о вакансии и возвращает строку
        с местом работы или `None`. Метод получает значение ключа "place_of_work"
        из словаря с данными о вакансии. Если значение равно `None`, то метод
        возвращает `None`. В противном случае метод получает значение ключа "title"
        из словаря со значением ключа "place_of_work". Полученное значение возвращается
        как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str | None: Строка с местом работы или `None`.
        """
        place_of_work = vacancy.get("place_of_work", None)
        return place_of_work.get("title", None) if place_of_work else None

    async def get_schedule(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения графика работы.

        Метод принимает на вход словарь с данными о вакансии и возвращает строку с
        графиком работы или `None`. Метод получает значение ключа "type_of_work" из
        словаря с данными о вакансии. Если значение равно `None`, то метод возвращает
        `None`. В противном случае метод получает значение ключа "title" из словаря со
        значением ключа "type_of_work" и вызывает метод `get_remote` с передачей ему
        полученного значения. Полученное значение возвращается как результат работы
        метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str | None: Строка с графиком работы или `None`.
        """
        schedule = vacancy.get("type_of_work", None)
        schedule = schedule.get("title", None) if schedule else None
        await self.get_remote(schedule)
        return schedule

    async def get_remote(self, schedule: str) -> bool:
        """
        Асинхронный метод для определения удаленной работы.

        Метод принимает на вход строку с графиком работы и возвращает булево значение,
        указывающее на то, является ли работа удаленной. Метод проверяет, равно ли
        переданное значение `None`. Если это так, то метод возвращает `False`.
        В противном случае метод проверяет, содержит ли переданная строка подстроку
        "Удаленн" или "Удалённ" с помощью функции `search` модуля `re`.
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

        Метод принимает на вход словарь с данными о вакансии и возвращает строку
        с опытом работы или `None`. Метод получает значение ключа "experience" из
        словаря с данными о вакансии. Если значение равно `None`, то метод возвращает
        `None`. В противном случае метод получает значение ключа "id" из словаря
        со значением ключа "experience", преобразует его в целое число и вызывает
        функцию `convert_experience` модуля `utils` с передачей ему полученного
        значения и строки "SuperJob".
        Полученное значение возвращается как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str | None: Строка с опытом работы или `None`.
        """
        experience = vacancy.get("experience", None)
        converted_experience = None
        if experience:
            experience_id = int(experience.get("id", None))
            converted_experience = utils.convert_experience(experience_id, "SuperJob")
        return converted_experience

    async def get_published_at(self, vacancy: dict) -> datetime.date | None:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Метод получает значение ключа "date_published" из словаря vacancy и преобразует
        его в формат даты. Возвращает эту дату.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        date = vacancy.get("date_published", None)
        return datetime.date.fromtimestamp(date) if date else None
