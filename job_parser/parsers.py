import os
import sys
import asyncio
import orjson
import datetime
import aiofiles
import httpx
from dateutil import parser
from typing import Optional
from dotenv import load_dotenv
import pytz

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

django.setup()

load_dotenv()


class ParserConfig:
    """Этот класс хранит параметры запросов к API SuperJob."""

    superjob_domen: str = "https://api.superjob.ru"
    superjob_api_version: str = "2.0"
    superjob_api_path: str = "vacancies"
    superjob_secret_key: str = os.getenv("SUPERJOB_SECRET_KEY")
    superjob_headers: dict = {"x-api-app-id": superjob_secret_key}
    superjob_url: str = f"{superjob_domen}/{superjob_api_version}/{superjob_api_path}/"

    headhunter_domen: str = "https://api.hh.ru"
    headhunter_api_path: str = "vacancies"
    headhunter_url: str = f"{headhunter_domen}/{headhunter_api_path}"

    zarplata_domen: str = "https://api.zarplata.ru"
    zarplata_api_path: str = "vacancies"
    zarplata_url: str = f"{zarplata_domen}/{zarplata_api_path}"


config = ParserConfig()


class Parser:
    """Основной класс парсера."""

    general_job_list: list[dict] = []

    async def create_session(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> str:
        """Отвечает за создание запросов к API.

        Args:
            url (str): URL - адрес API.
            headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.
            params (Optional[dict], optional): Параметры запроса. По умолчанию None.

        Returns:
            str: Контент в виде строки.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
            data = response.content.decode()
        return data

    async def get_vacancies(
        self,
        url: str,
        params: dict,
        pages: int,
        total_pages: str,
        headers: Optional[dict] = None,
    ) -> list:
        """Отвечает за получение постраничное получение вакансий.

        Args:
            url (str): URL - адрес API.
            params (dict): Параметры запроса.
            page_range (int): Диапазон страниц (максимум 20)
            total_pages (str): Строковое представление ключа словаря
            с общим количеством страниц, которые вернул сервер. Т.к у каждого API
            разное название этого параметра, его нужно передать здесь.
            Необходимо для проверки на последнюю страницу.
            headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.

        Returns:
            list: _description_
        """
        job_list = []
        for page in range(pages):  # Постраничный вывод вакансий
            params["page"] = page
            page += 1
            try:
                data = await self.create_session(url=url, params=params, headers=headers)
                json_data = orjson.loads(data)
                job_list.append(json_data)
            except httpx.RequestError as exc:
                return f"Адрес {exc.request.url!r} вернул неверный ответ {exc}"

            if (job_list[0][total_pages] - page) <= 1:  # Проверка на последнюю страницу
                break

        return job_list

    @staticmethod
    def convert_date(date: str | datetime.date | int) -> str | datetime.date | int:
        """Проверяет формат даты и при необходимости конвертирует его.

        Args:
            date (str | datetime.date | int): Дата.

        Returns:
            str | datetime.date | int: Дата.
        """
        if isinstance(date, datetime.date):
            converted_to_datetime = datetime.datetime.combine(
                date, datetime.time()
            ).timestamp()
            return converted_to_datetime
        elif isinstance(date, str):
            converted_from_str = datetime.datetime.strptime(date, "%Y-%m-%d")
            converted_to_datetime = datetime.datetime.combine(
                converted_from_str, datetime.time()
            ).timestamp()
            return converted_to_datetime
        else:
            return date

    @staticmethod
    def check_date(date_from: str, date_to: str) -> datetime.date:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str): Дата от.
            date_to (str): Дата до.

        Returns:
            datetime.date: Время задаваемое по умолчанию.
        """
        if date_from == "":
            date_from = datetime.date.today() - datetime.timedelta(days=10)
        if date_to == "":
            date_to = datetime.date.today()
        return date_from, date_to

    @staticmethod
    def sort_by_date(job_list: list[dict], key: str) -> list[dict]:
        """Сортирует список вакансий по дате.

        Args:
            job_list (list[dict]): Список вакансий.
            key (str): Ключь, по которому сортируем.

        Returns:
            list[dict]: Сортированный список вакансий.
        """
        sorted_list = sorted(job_list, key=lambda _dict: _dict[key], reverse=True)
        return sorted_list

    @staticmethod
    def sort_by_title(job_list: list[dict], title: str) -> list[dict]:
        """Сортирует список вакансий по наличию в заголовке
        вакансии ключевого слова.

        Args:
            job_list (list[dict]): Список вакансий.
            title (str): Ключевое слово, по которому сортируем.

        Returns:
            list[dict]: Сортированный список вакансий.
        """
        sorted_list = []
        for job in job_list:
            if title in job["title"]:
                sorted_list.append(job)
        return sorted_list


class Headhunter(Parser):
    def __init__(
        self,
        city_from_db: str,
        job: str,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> None:
        self.city_from_db = city_from_db
        self.job = job
        self.date_from, self.date_to = self.check_date(date_from, date_to)

        # Формируем параметры запроса к API Headhunter
        self.hh_params = {
            "text": f"NAME:{self.job}",
            "area": self.city_from_db,
            "per_page": 100,
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

    async def get_vacancy_from_headhunter(self) -> dict:
        """Формирует словарь с основными полями вакансий с сайта HeadHunter

        Returns:
            dict: Словарь с основными полями вакансий
        """
        job_list = await self.get_vacancies(
            url=config.headhunter_url,
            params=self.hh_params,
            pages=20,
            total_pages="pages",
        )

        job_dict = {}
        # Формируем словарь с вакансиями
        for job in job_list[0]["items"]:
            job_dict["job_board"] = "HeadHunter"
            job_dict["url"] = job["alternate_url"]
            job_dict["title"] = job["name"]
            if job["salary"]:
                job_dict["salary_from"] = job["salary"]["from"]
                job_dict["salary_to"] = job["salary"]["to"]
                job_dict["salary_currency"] = job["salary"]["currency"]
            if job["snippet"]:
                job_dict["responsibility"] = job["snippet"]["responsibility"]
            if job["area"]:
                job_dict["city"] = job["area"]["name"]
            if job["employer"]:
                job_dict["company"] = job["employer"]["name"]

            # Конвертируем дату в удобочитаемый вид
            published_date = parser.parse(job["published_at"]).replace(tzinfo=pytz.UTC)
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта Headhunter завершен")
        return job_dict


class SuperJob(Parser):
    def __init__(
        self,
        city: str,
        job: str,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> None:
        self.city = city
        self.job = job
        self.date_from, self.date_to = self.check_date(date_from, date_to)

        # Формируем параметры запроса к API SuperJob
        self.sj_params = {
            "keyword": self.job,
            "town": self.city,
            "count": 100,
            "date_published_from": self.convert_date(self.date_from),
            "date_published_to": self.convert_date(self.date_to),
        }

    async def get_vacancy_from_superjob(self) -> dict:
        """Формирует словарь с основными полями вакансий с сайта SuperJob

        Returns:
            dict: Словарь с основными полями вакансий
        """
        job_list = await self.get_vacancies(
            url=config.superjob_url,
            params=self.sj_params,
            pages=5,
            total_pages="total",
            headers=config.superjob_headers,
        )

        job_dict = {}
        # Формируем словарь с вакансиями
        for job in job_list[0]["objects"]:
            job_dict["job_board"] = "SuperJob"
            job_dict["url"] = job["link"]
            job_dict["title"] = job["profession"]
            job_dict["salary_from"] = job["payment_from"]
            job_dict["salary_to"] = job["payment_to"]
            job_dict["salary_currency"] = job["currency"]
            if job["candidat"]:
                job_dict["responsibility"] = job["candidat"]
            if job["town"]:
                job_dict["city"] = job["town"]["title"]
            job_dict["company"] = job["firm_name"]

            # Конвертируем дату в удобочитаемый вид
            published_date = datetime.datetime.fromtimestamp(
                job["date_published"]
            ).replace(tzinfo=pytz.UTC)
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта SuperJob завершен")
        return job_dict


class Zarplata(Parser):
    def __init__(
        self,
        city_from_db: str,
        job: str,
        date_from: datetime.date,
        date_to: datetime.date,
    ) -> None:
        self.city_from_db = city_from_db
        self.job = job
        self.date_from, self.date_to = self.check_date(date_from, date_to)

        # Формируем параметры запроса к API Zarplata
        self.zp_params = {
            "text": f"NAME:{self.job}",
            "area": self.city_from_db,
            "per_page": 100,
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

    async def get_vacancy_from_zarplata(self) -> dict:
        """Формирует словарь с основными полями вакансий с сайта Zarplata

        Returns:
            dict: Словарь с основными полями вакансий
        """
        job_list = await self.get_vacancies(
            url=config.zarplata_url, params=self.zp_params, pages=20, total_pages="pages"
        )

        job_dict = {}
        # Формируем словарь с вакансиями
        for job in job_list[0]["items"]:
            job_dict["job_board"] = "Zarplata"
            job_dict["url"] = job["alternate_url"]
            job_dict["title"] = job["name"]
            if job["salary"]:
                job_dict["salary_from"] = job["salary"]["from"]
                job_dict["salary_to"] = job["salary"]["to"]
                job_dict["salary_currency"] = job["salary"]["currency"]
            if job["snippet"]:
                job_dict["responsibility"] = job["snippet"]["responsibility"]
            if job["area"]:
                job_dict["city"] = job["area"]["name"]
            if job["employer"]:
                job_dict["company"] = job["employer"]["name"]

            # Конвертируем дату в удобочитаемый вид
            published_date = parser.parse(job["published_at"]).replace(tzinfo=pytz.UTC)
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта Zarplata завершен")
        return job_dict


async def run(
    city: Optional[str] = "Москва",
    city_from_db: Optional[int] = 1,
    job: Optional[str] = "Python",
    date_to: Optional[str] = "",
    date_from: Optional[str] = "",
    title_search: Optional[bool] = False,
) -> list[dict]:
    """Отвечает за запуск парсера.

    Args:
        city (Optional[str], optional): Город. По умолчанию "Москва".
        city_from_db (Optional[int], optional): Код города из базы данных.
        Необходим для поиска в API HeadHUnter. По умолчанию 1.
        job (Optional[str], optional): Специальность. По умолчанию "Python".
        date_to (Optional[datetime.date], optional): Дата до. По умолчанию сегодня.
        date_from (Optional[datetime.date], optional): Дата от.
        По умолчанию высчитывается по формуле: 'Сегодня - 10 дней'.
        title_search (Optional[bool]): Если True, то поиск идет по заголовкам вакансий.

    Returns:
        list[dict]: Список словарей с вакансиями.
    """

    hh = Headhunter(
        city_from_db=city_from_db,
        job=job,
        date_from=date_from,
        date_to=date_to,
    )
    sj = SuperJob(
        city=city,
        job=job,
        date_from=date_from,
        date_to=date_to,
    )
    zp = Zarplata(
        city_from_db=city_from_db,
        job=job,
        date_from=date_from,
        date_to=date_to,
    )

    # Очищаем список вакансий
    Parser.general_job_list.clear()

    # Оборачиваем сопрограммы в задачи
    task1 = asyncio.create_task(hh.get_vacancy_from_headhunter())
    task2 = asyncio.create_task(sj.get_vacancy_from_superjob())
    task3 = asyncio.create_task(zp.get_vacancy_from_zarplata())

    # Запускаем задачи
    await asyncio.gather(task1, task2, task3)

    # Сортируем получемнный список вакансий
    sorted_job_list_by_date = Parser.sort_by_date(Parser.general_job_list, "published_at")
    if title_search:
        sorted_job_list_by_date = Parser.sort_by_title(sorted_job_list_by_date, job)
    # print(f"Количество вакансий: {len(sorted_job_list)}", sorted_job_list)
    return sorted_job_list_by_date


async def create_session(
    url: str,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
) -> str:
    """Отвечает за создание запросов к API.

    Args:
        url (str): URL - адрес API.
        headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.
        params (Optional[dict], optional): Параметры запроса. По умолчанию None.

    Returns:
        str: Контент в виде строки.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url=url, headers=headers, params=params)
        data = response.content.decode()
    print(data)
    return data


if __name__ == "__main__":
    asyncio.run(run())
