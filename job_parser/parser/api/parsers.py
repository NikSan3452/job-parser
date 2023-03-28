import datetime

from logger import logger, setup_logging

from .base_parser import Parser
from .config import ParserConfig, RequestConfig
from .utils import Utils

# Логирование
setup_logging()

config = ParserConfig()
utils = Utils()


class Headhunter(Parser):
    """Парсер Headhunter."""

    def __init__(self, params: RequestConfig) -> None:
        self.params = params

    @logger.catch(message="Ошибка в методе Headhunter.get_request_params()")
    async def get_request_params(self) -> dict:
        """Формирует параметры запросов к API.

        Returns:
            dict: словарь с параметрами.
        """
        city_from_db = self.params.city_from_db
        job = self.params.job
        experience = "noExperience"
        remote = self.params.remote
        date_from, date_to = await utils.check_date(
            self.params.date_from, self.params.date_to
        )

        # Формируем параметры запроса к API Headhunter
        hh_params = {
            "text": job,
            "per_page": 100,
            "date_from": date_from,
            "date_to": date_to,
        }

        if city_from_db:
            hh_params["area"] = city_from_db

        if remote:
            hh_params["schedule"] = "remote"

        if self.params.experience > 0:
            experience = await utils.convert_experience(self.params.experience)
            hh_params["experience"] = experience

        return hh_params

    @logger.catch(message="Ошибка в методе Headhunter.get_vacancy_from_headhunter()")
    async def get_vacancy_from_headhunter(
        self, url: str = config.headhunter_url, job_board: str = "HeadHunter"
    ) -> dict:
        """Формирует словарь с основными полями вакансий с сайта HeadHunter

        Returns:
            dict: Словарь с основными полями вакансий
        """
        hh_params = await self.get_request_params()

        job_list: list[dict] = await self.get_vacancies(
            url=url, params=hh_params, pages=20, items="items"
        )

        job_dict: dict = {}
        # Формируем словарь с вакансиями
        for job in job_list:
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
            published_date = datetime.datetime.strptime(
                job["published_at"], "%Y-%m-%dT%H:%M:%S%z"
            ).date()
            job_dict["published_at"] = published_date

            # Добавляем словарь с вакансией в общий список всех вакансий
            Parser.general_job_list.append(job_dict.copy())

        if url == config.headhunter_url:
            logger.debug("Сбор вакансий с Headhunter завершен")

        return job_dict


class SuperJob(Parser):
    """Парсер SuperJob."""

    def __init__(self, params: RequestConfig) -> None:
        self.params = params

    @logger.catch(message="Ошибка в методе SuperJob.get_request_params()")
    async def get_request_params(self) -> dict:
        """Формирует параметры запросов к API.

        Returns:
            dict: словарь с параметрами.
        """
        city = self.params.city
        job = self.params.job
        date_from, date_to = await utils.check_date(
            self.params.date_from, self.params.date_to
        )
        remote = self.params.remote

        # Формируем параметры запроса к API SuperJob
        sj_params = {
            "keyword": job,
            "count": 100,
            "date_published_from": await utils.convert_date(date_from),
            "date_published_to": await utils.convert_date(date_to),
        }

        if city:
            sj_params["town"] = city

        if remote:
            sj_params["place_of_work"] = 2

        if self.params.experience > 0:
            sj_params["experience"] = self.params.experience

        return sj_params

    @logger.catch(message="Ошибка в методе SuperJob.get_vacancy_from_superjob()")
    async def get_vacancy_from_superjob(self) -> dict:
        """Формирует словарь с основными полями вакансий с сайта SuperJob

        Returns:
            dict: Словарь с основными полями вакансий
        """
        sj_params = await self.get_request_params()

        job_list = await self.get_vacancies(
            url=config.superjob_url,
            params=sj_params,
            pages=5,
            headers=config.superjob_headers,
            items="objects",
        )

        job_dict: dict = {}
        # Формируем словарь с вакансиями
        for job in job_list:
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

            if job["firm_name"]:
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
            published_date = datetime.date.fromtimestamp(job["date_published"])
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
        job_dict = await super().get_vacancy_from_headhunter(
            config.zarplata_url, "Zarplata"
        )
        logger.debug("Сбор вакансий с Zarplata завершен")
        return job_dict


class Trudvsem(Parser):
    """Парсер Trudvsem."""

    def __init__(self, params: RequestConfig) -> None:
        self.params = params

    @logger.catch(message="Ошибка в методе Trudvsem.get_request_params()")
    async def get_request_params(self) -> dict:
        """Формирует параметры запросов к API.

        Returns:
            dict: словарь с параметрами.
        """
        job = self.params.job
        date_from, date_to = await utils.check_date(
            self.params.date_from, self.params.date_to
        )

        # Формируем параметры запроса к API Trudvsem
        tv_params = {
            "text": job,
            "limit": 100,
            "offset": 0,
            "modifiedFrom": await utils.convert_date_for_trudvsem(date_from),
            "modifiedTo": await utils.convert_date_for_trudvsem(date_to),
        }

        if self.params.experience > 0:
            (
                tv_params["experienceFrom"],
                tv_params["experienceTo"],
            ) = await utils.convert_experience_for_trudvsem(self.params.experience)

        return tv_params

    @logger.catch(message="Ошибка в методе Trudvsem.get_vacancy_from_trudvsem()")
    async def get_vacancy_from_trudvsem(self) -> dict:
        """Формирует словарь с основными полями вакансий с сайта Trudvsem

        Returns:
            dict: Словарь с основными полями вакансий
        """
        tv_params = await self.get_request_params()
        job_list: list[dict] = await self.get_vacancies(
            url=config.trudvsem_url, params=tv_params, pages=20, items="results"
        )

        job_dict: dict = {}
        # Формируем словарь с вакансиями
        for job in job_list:
            job_dict["job_board"] = "Trudvsem"

            vacancy: dict = job.get("vacancy", None)

            if vacancy is not None:
                job_dict["url"] = vacancy.get("vac_url")

                job_dict["title"] = vacancy.get("job-name")

                if vacancy.get("salary_min"):
                    job_dict["salary_from"] = vacancy.get("salary_min")
                else:
                    job_dict["salary_from"] = None

                job_dict["salary_currency"] = "RUR"

                if vacancy.get("salary_max"):
                    job_dict["salary_to"] = vacancy.get("salary_max")
                else:
                    job_dict["salary_to"] = None

                if vacancy.get("duty"):
                    job_dict["responsibility"] = vacancy.get("duty")
                else:
                    job_dict["responsibility"] = "Нет описания"

                if vacancy.get("requirement"):
                    if vacancy["requirement"]["education"]:
                        education = vacancy["requirement"]["education"]
                    if vacancy["requirement"]["experience"]:
                        experience = vacancy["requirement"]["experience"]
                        job_dict[
                            "requirement"
                        ] = f"{education} образование, опыт работы (лет): {experience}"
                else:
                    job_dict["requirement"] = "Нет описания"

                job_dict["city"] = vacancy["addresses"]["address"][0]["location"]

                job_dict["company"] = vacancy["company"]["name"]

                if vacancy.get("schedule"):
                    job_dict["type_of_work"] = vacancy.get("schedule")
                else:
                    job_dict["type_of_work"] = "Не указано"

                # Конвертируем дату в удобочитаемый вид
                published_date = datetime.datetime.strptime(
                    vacancy.get("creation-date", ""), "%Y-%m-%d"
                ).date()
                job_dict["published_at"] = published_date

                if self.params.city:  # Если при поиске указан город ищем его в адресе
                    if self.params.city in job_dict.get("city", "").lower():
                        # Добавляем словарь с вакансией в общий список всех вакансий
                        Parser.general_job_list.append(job_dict.copy())
                else:
                    Parser.general_job_list.append(job_dict.copy())

        logger.debug("Сбор вакансий с Trudvsem завершен")

        return job_dict
