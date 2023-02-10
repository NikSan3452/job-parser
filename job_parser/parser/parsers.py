import os
import asyncio
import orjson
import datetime
import httpx
from dateutil import parser
from typing import Optional
from dotenv import load_dotenv
import pytz
from dataclasses import dataclass

load_dotenv()


class ParserConfig:
    """Этот класс хранит параметры запросов к API."""

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


class Utils:
    """Класс со вспомогательными методами"""

    @staticmethod
    def convert_date(date: str | datetime.date) -> float:
        """Проверяет формат даты и при необходимости конвертирует его.

        Args:
            date (str | datetime.date): Дата.

        Returns:
            float: Конвертированная дата.
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

    @staticmethod
    def check_date(date_from: str, date_to: str) -> datetime.date | str:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str): Дата от.
            date_to (str): Дата до.

        Returns:
            datetime.date | str: Время задаваемое по умолчанию.
        """
        if date_from == "" or date_from is None:
            date_from = datetime.date.today() - datetime.timedelta(days=3)
        if date_to == "" or date_to is None:
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
        sorted_list: list[dict] = sorted(
            job_list, key=lambda _dict: _dict[key], reverse=True
        )
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
        sorted_list: list[dict] = []
        for job in job_list:
            if title in job["title"]:
                sorted_list.append(job)
        return sorted_list

    @staticmethod
    def convert_experience(experience: int) -> str:
        """Конвертирует значения опыта работы в понятный
        для API HeadHunter и Zarplata вид.

        Args:
            experience (int): Опыт.

        Returns:
            str: Конвертированный опыт.
        """
        if experience == 1:
            experience = "noExperience"
        elif experience == 2:
            experience = "between1And3"
        elif experience == 3:
            experience = "between3And6"
        elif experience == 4:
            experience = "moreThan6"
        return experience

    @staticmethod
    def sorted_by_remote_work(remote: bool, job_list: list[dict]):
        sorted_list: list[dict] = []
        if remote:
            for job in job_list:
                if job.get("type_of_work") == "Удаленная работа":
                    sorted_list.append(job)
                elif job.get("place_of_work") == "Удалённая работа (на дому)":
                    sorted_list.append(job)
        return sorted_list


@dataclass
class RequestParams:
    city: Optional[str]
    city_from_db: Optional[int]
    job: Optional[str]
    date_to: Optional[str | datetime.date]
    date_from: Optional[str | datetime.date]
    experience: int
    utils: Utils


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
    ) -> list[dict] | str:
        """Отвечает за постраничное получение вакансий.

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
            list[dict] | str: Список вакансий или исключение.
        """
        job_list: list[dict] = []
        for page in range(pages):  # Постраничный вывод вакансий
            params["page"] = page
            page += 1
            try:
                data = await self.create_session(url=url, params=params, headers=headers)
                json_data = orjson.loads(data)
                job_list.append(json_data)

                if (
                    job_list[0][total_pages] - page
                ) <= 1:  # Проверка на последнюю страницу
                    break
            except httpx.RequestError as exc:
                print(f"Адрес {exc.request.url!r} вернул неверный ответ {exc}")

        return job_list


class Headhunter(Parser):
    def __init__(self, params: RequestParams) -> None:
        self.utils = params.utils
        self.city_from_db = params.city_from_db
        self.job = params.job
        self.date_from, self.date_to = self.utils.check_date(
            params.date_from, params.date_to
        )
        self.experience = params.experience

        # Формируем параметры запроса к API Headhunter
        self.hh_params = {
            "text": f"NAME:{self.job}",
            "per_page": 100,
            "date_from": self.date_from,
            "date_to": self.date_to,
        }

        if self.city_from_db:
            self.hh_params["area"] = self.city_from_db

        if params.experience > 0:
            self.experience = self.utils.convert_experience(experience=params.experience)
            self.hh_params["experience"] = self.experience

    async def get_vacancy_from_headhunter(
        self, url: ParserConfig = config.headhunter_url, job_board: str = "HeadHunter"
    ) -> dict:
        """Формирует словарь с основными полями вакансий с сайта HeadHunter

        Returns:
            dict: Словарь с основными полями вакансий
        """
        job_list = await self.get_vacancies(
            url=url,
            params=self.hh_params,
            pages=20,
            total_pages="pages",
        )

        job_dict = {}
        # Формируем словарь с вакансиями
        for job in job_list[0]["items"]:
            job_dict["job_board"] = job_board
            job_dict["url"] = job["alternate_url"]
            job_dict["title"] = job["name"]

            if job["salary"]:
                job_dict["salary_from"] = job["salary"]["from"]
                job_dict["salary_to"] = job["salary"]["to"]
                job_dict["salary_currency"] = job["salary"]["currency"]
            else:
                job_dict["salary_from"] = None
                job_dict["salary_to"] = None

            if job["snippet"]:
                job_dict["responsibility"] = job["snippet"]["responsibility"]
                job_dict["requirement"] = job["snippet"]["requirement"]
            else:
                job_dict["responsibility"] = "Нет описания"
                job_dict["requirement"] = "Нет описания"

            job_dict["city"] = job["area"]["name"]
            job_dict["company"] = job["employer"]["name"]

            if job["schedule"]:
                job_dict["type_of_work"] = job["schedule"]["name"]
            else:
                job_dict["type_of_work"] = "Не указано"

            # Конвертируем дату в удобочитаемый вид
            published_date = parser.parse(job["published_at"]).replace(tzinfo=pytz.UTC)
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта Headhunter завершен")
        return job_dict


class SuperJob(Parser):
    def __init__(self, params: RequestParams) -> None:
        self.utils = params.utils
        self.city = params.city
        self.job = params.job
        self.date_from, self.date_to = self.utils.check_date(
            params.date_from, params.date_to
        )

        # Формируем параметры запроса к API SuperJob
        self.sj_params = {
            "keyword": self.job,
            "count": 100,
            "date_published_from": self.utils.convert_date(self.date_from),
            "date_published_to": self.utils.convert_date(self.date_to),
        }

        if self.city:
            self.sj_params["town"] = self.city

        if params.experience > 0:
            self.sj_params["experience"] = params.experience

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

            if job["payment_from"]:
                job_dict["salary_from"] = job["payment_from"]
            else:
                job_dict["salary_from"] = None

            if job["payment_to"]:
                job_dict["salary_to"] = job["payment_to"]
            else:
                job_dict["salary_to"] = None

            if job["currency"]:
                job_dict["salary_currency"] = job["currency"]
            else:
                job_dict["salary_currency"] = "Валюта не указана"

            if job["work"]:
                job_dict["responsibility"] = job["work"]
            else:
                job_dict["responsibility"] = "Нет описания"

            if job["candidat"]:
                job_dict["requirement"] = job["candidat"]
            else:
                job_dict["requirement"] = "Нет описания"

            if job["town"]:
                job_dict["city"] = job["town"]["title"]
            job_dict["company"] = job["firm_name"]

            if job["type_of_work"]:
                job_dict["type_of_work"] = job["type_of_work"]["title"]
            else:
                job_dict["type_of_work"] = "Не указано"

            if job["place_of_work"]:
                job_dict["place_of_work"] = job["place_of_work"]["title"]
            else:
                job_dict["place_of_work"] = "Нет описания"

            if job["experience"]:
                job_dict["experience"] = job["experience"]["title"]
            else:
                job_dict["experience"] = "Не указано"

            # Конвертируем дату в удобочитаемый вид
            published_date = datetime.datetime.fromtimestamp(
                job["date_published"]
            ).replace(tzinfo=pytz.UTC)
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта SuperJob завершен")
        return job_dict


class Zarplata(Headhunter):
    def __init__(self, params: RequestParams) -> None:
        super().__init__(params)

    async def get_vacancy_from_zarplata(self) -> dict:
        job_dict = await super().get_vacancy_from_headhunter(
            config.zarplata_url, "Zarplata"
        )
        print("Сбор вакансий с сайта Zarplata завершен")
        return job_dict


async def run(
    city: Optional[str] = None,
    city_from_db: Optional[int] = None,
    job: Optional[str] = "Python",
    date_to: Optional[str | datetime.date] = None,
    date_from: Optional[str | datetime.date] = None,
    title_search: Optional[bool] = False,
    experience: int = 0,
    remote: Optional[bool] = False,
) -> list[dict]:
    """Отвечает за запуск парсера.

    Args:
        city (Optional[str], optional): Город. По умолчанию "Москва".
        city_from_db (Optional[int], optional): Код города из базы данных.
        Необходим для поиска в API HeadHUnter. По-умолчанию 1.
        job (Optional[str], optional): Специальность. По-умолчанию "Python".
        date_to (Optional[datetime.date], optional): Дата до. По-умолчанию сегодня.
        date_from (Optional[datetime.date], optional): Дата от.
        По-умолчанию высчитывается по формуле: 'Сегодня - 10 дней'.
        title_search (Optional[bool]): Если True, то поиск идет по заголовкам вакансий.
        experience (int): Опыт работы. По-умолчанию False.
        remote (Optional[bool]): Если True, то поиск идет по удаленной работе.
    Returns:
        list[dict]: Список словарей с вакансиями.
    """

    utils = Utils()

    params = RequestParams(
        city=city,
        city_from_db=city_from_db,
        job=job,
        date_from=date_from,
        date_to=date_to,
        experience=experience,
        utils=utils,
    )

    hh = Headhunter(params)
    sj = SuperJob(params)
    zp = Zarplata(params)

    # Очищаем список вакансий
    Parser.general_job_list.clear()

    # Оборачиваем сопрограммы в задачи
    task1 = asyncio.create_task(hh.get_vacancy_from_headhunter())
    task2 = asyncio.create_task(sj.get_vacancy_from_superjob())
    task3 = asyncio.create_task(zp.get_vacancy_from_zarplata())

    # Запускаем задачи
    await asyncio.gather(task1, task2, task3)

    # Сортируем получемнный список вакансий
    sorted_job_list = utils.sort_by_date(Parser.general_job_list, "published_at")
    if title_search:
        sorted_job_list = utils.sort_by_title(sorted_job_list, job)
    if remote:
        sorted_job_list = utils.sorted_by_remote_work(remote, sorted_job_list)
    if remote and title_search:
        sorted_job_list_title = utils.sort_by_title(sorted_job_list, job)
        sorted_job_list = utils.sorted_by_remote_work(remote, sorted_job_list_title)

    # print(f"Количество вакансий: {len(sorted_job_list)}", sorted_job_list)
    return sorted_job_list


if __name__ == "__main__":
    asyncio.run(run())
