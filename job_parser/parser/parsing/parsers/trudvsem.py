import datetime
import re

from logger import setup_logging

from ..config import ParserConfig
from ...utils import Utils
from .base import Parser, Vacancy

# Логирование
setup_logging()

utils = Utils()


class Trudvsem(Parser):
    """
    Класс для парсинга вакансий с сайта Trudvsem.

    Наследуется от класса Parser.
    Класс Trudvsem предназначен для парсинга вакансий с сайта Trudvsem.
    Он содержит методы для получения информации о вакансиях, такие как URL-адрес,
    название, зарплата, город и другие. Эти методы реализованы с учетом особенностей
    API сайта Trudvsem.
    """

    def __init__(self, config: ParserConfig) -> None:
        """
        Инициализация экземпляра класса Trudvsem.

        Attributes:
            config (ParserConfig): Экземпляр класса ParserConfig.
        """
        super().__init__(config, "tv")

    async def parsing_vacancy_trudvsem(self) -> Vacancy | None:
        """
        Асинхронный метод для парсинга вакансий с сайта Trudvsem.

        Метод получает параметры запроса с помощью метода get_request_params и вызывает
        метод vacancy_parsing родительского класса Parser.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        return await super().vacancy_parsing()

    async def get_url(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения URL-адреса вакансии.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "vac_url".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        return vacancy.get("vac_url", None) if vacancy else None

    async def get_title(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия вакансии.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "job-name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        return vacancy.get("job-name", None) if vacancy else None

    async def get_salary_from(self, vacancy: dict) -> int | None:
        """
        Асинхронный метод для получения минимальной зарплаты.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "salary_min".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        salary_from = vacancy.get("salary_min", None)
        if int(salary_from) == 0:
            salary_from = None
        return int(salary_from) if salary_from else None

    async def get_salary_to(self, vacancy: dict) -> int | None:
        """
        Асинхронный метод для получения максимальной зарплаты.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "salary_max".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            int | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        salary_to = vacancy.get("salary_max", None)
        if int(salary_to) == 0:
            salary_to = None
        return int(salary_to) if salary_to else None

    async def get_salary_currency(self, vacancy: dict) -> str:
        """
        Асинхронный метод для получения валюты зарплаты.

        Метод возвращает строку "RUR".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str: Валюта зарплаты по вакансии.
        """
        salary_currency = "RUR"
        return salary_currency

    async def get_description(self, vacancy: dict) -> str:
        """
        Асинхронный метод для получения описания вакансии.

        Метод принимает на вход словарь с данными о вакансии и возвращает строку
        с описанием. Метод получает значение ключа "vacancy" из словаря с данными
        о вакансии. Если значение равно `None`, то метод возвращает строку
        "Нет описания". В противном случае метод получает значение ключа "duty"
        из словаря со значением ключа "vacancy".
        Полученное значение возвращается как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str: Строка с описанием вакансии.
        """
        vacancy_ = vacancy.get("vacancy", None)
        description = None
        if vacancy_:
            description = vacancy_.get("duty", None)
        return description if description else "Нет описания"

    async def get_city(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения города.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "location".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        addresses = vacancy.get("addresses") if vacancy else None
        return vacancy["addresses"]["address"][0]["location"] if addresses else None

    async def get_company(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения названия компании.

        Метод получает значение ключа "vacancy" из словаря vacancy и возвращает значение
        ключа "name".

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        vacancy = vacancy.get("vacancy", None)
        company = vacancy.get("company") if vacancy else None
        return company.get("name", None) if company else None

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
        vacancy = vacancy.get("vacancy", None)
        employment = vacancy.get("employment", None)
        return employment if employment else None

    async def get_schedule(self, vacancy: dict) -> str | None:
        """
        Асинхронный метод для получения графика работы.

        Метод принимает на вход словарь с данными о вакансии и возвращает строку
        с графиком работы или `None`. Метод получает значение ключа "vacancy" из
        словаря с данными о вакансии. Если значение равно `None`, то метод возвращает
        `None`. В противном случае метод получает значение ключа "schedule" из словаря
        со значением ключа "vacancy" и вызывает метод `get_remote` с передачей ему
        полученного значения.
        Полученное значение возвращается как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str | None: Строка с графиком работы или `None`.
        """
        vacancy_ = vacancy.get("vacancy", None)
        schedule = vacancy_.get("schedule", None)
        schedule = schedule if schedule else None
        await self.get_remote(schedule)
        return schedule

    async def get_remote(self, schedule: str | None) -> bool:
        """
        Асинхронный метод для определения удаленной работы.

        Метод принимает на вход строку с графиком работы и возвращает булево значение,
        указывающее на то, является ли работа удаленной. Метод проверяет, равно ли
        переданное значение `None`. Если это так, то метод возвращает `False`.
        В противном случае метод проверяет, содержит ли переданная строка подстроку
        "Удаленн" или "Удалённ" с помощью функции `search` модуля `re`. Если подстрока
        найдена, то метод возвращает `True`, иначе - `False`.

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
        с опытом работы или `None`. Метод получает значение ключа "vacancy" из словаря
        с данными о вакансии. Если значение равно `None`, то метод возвращает `None`.
        В противном случае метод получает значение ключа "requirement" из словаря со
        значением ключа "vacancy". Если значение равно `None`, то метод возвращает
        `None`. В противном случае метод получает значение ключа "experience" из
        словаря со значением ключа "requirement". Если полученное значение является
        строкой, то метод проходит по всем символам строки и проверяет, является ли
        символ цифрой. Если символ является цифрой, то он преобразуется в целое число.
        Затем метод вызывает функцию `convert_experience` модуля `utils` с передачей
        ему полученного значения и строки "Trudvsem".
        Полученное значение возвращается как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            str | None: Строка с опытом работы или `None`.
        """
        vacancy_ = vacancy.get("vacancy", None)
        converted_experience = None
        if vacancy_:
            requirement = vacancy_.get("requirement", None)
            if requirement:
                experience = requirement.get("experience", None)
                if isinstance(experience, str):
                    for char in experience:
                        if char.isdigit():
                            experience = int(char)
                converted_experience = utils.convert_experience(experience, "Trudvsem")
        return converted_experience

    async def get_published_at(self, vacancy: dict) -> datetime.date:
        """
        Асинхронный метод для получения даты публикации вакансии.

        Args:
            vacancy (dict): Словарь с информацией о вакансии.

        Returns:
            datetime.date | None: Дата публикации вакансии или None, если дата
            отсутствует.
        """
        return datetime.date.today()
