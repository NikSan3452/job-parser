import pytz
import datetime

from dateutil import parser
from .utils import Utils
from .config import ParserConfig, RequestConfig
from .base_parser import Parser
from logger import setup_logging, logger

# Логирование
setup_logging()

config = ParserConfig()
utils = Utils()


class Headhunter(Parser):
    """Парсер Headhunter."""

    def __init__(self, params: RequestConfig) -> None:
        self.city_from_db = params.city_from_db
        self.job = params.job
        self.date_from, self.date_to = utils.check_date(params.date_from, params.date_to)
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
            self.experience = utils.convert_experience(experience=params.experience)
            self.hh_params["experience"] = self.experience

    @logger.catch(message="Ошибка в методе Headhunter.get_vacancy_from_headhunter()")
    async def get_vacancy_from_headhunter(
        self, url: str = config.headhunter_url, job_board: str = "HeadHunter"
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

        if url == config.headhunter_url:
            logger.debug("Сбор вакансий с Headhunter завершен")
            
        return job_dict


class SuperJob(Parser):
    """Парсер SuperJob."""

    def __init__(self, params: RequestConfig) -> None:
        self.city = params.city
        self.job = params.job
        self.date_from, self.date_to = utils.check_date(params.date_from, params.date_to)

        # Формируем параметры запроса к API SuperJob
        self.sj_params = {
            "keyword": self.job,
            "count": 100,
            "date_published_from": utils.convert_date(self.date_from),
            "date_published_to": utils.convert_date(self.date_to),
        }

        if self.city:
            self.sj_params["town"] = self.city

        if params.experience > 0:
            self.sj_params["experience"] = params.experience

    @logger.catch(message="Ошибка в методе SuperJob.get_vacancy_from_superjob()")
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
            published_date = datetime.datetime.fromtimestamp(job["date_published"]).replace(
                tzinfo=pytz.UTC
            )
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        logger.debug("Сбор вакансий с SuperJob завершен")
        return job_dict


class Zarplata(Headhunter):
    """Парсер Zarplata."""

    def __init__(self, params: RequestConfig) -> None:
        super().__init__(params)

    @logger.catch(message="Ошибка в методе Zarplata.get_vacancy_from_zarplata()")
    async def get_vacancy_from_zarplata(self) -> dict:
        """Отвечает за получение вакансий с сайта Zarplata.

        Returns:
            dict: Словарь с вакансиями.
        """
        job_dict = await super().get_vacancy_from_headhunter(config.zarplata_url, "Zarplata")
        logger.debug("Сбор вакансий с Zarplata завершен")
        return job_dict
