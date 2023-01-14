import os
import sys
import asyncio
import orjson
import datetime
import aiofiles
import httpx
import dataclasses
from dateutil import parser
from typing import Optional
from dotenv import load_dotenv

from django.db import DatabaseError
from asgiref.sync import sync_to_async

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

django.setup()


from parser.models import City


# async def add_cities():
#     city_list = get_city_list()
#     for hh_id, city in city_list.items():
#         try:
#             await City.objects.acreate(hh_id=hh_id, city=city)
#         except DatabaseError:
#             pass

# asyncio.run(add_cities())


load_dotenv()


@dataclasses.dataclass
class ParserData:
    HEADHUNTER_DOMEN: str = "https://api.hh.ru"
    HEADHUNTER_API_PATH: str = "vacancies"
    HEADHUNTER_URL = f"{HEADHUNTER_DOMEN}/{HEADHUNTER_API_PATH}"

    SUPERJOB_DOMEN: str = "https://api.superjob.ru"
    SUPERJOB_API_VERSION: str = "2.0"
    SUPERJOB_API_PATH: str = "vacancies"
    SUPERJOB_SECRET_KEY: str = os.getenv("SUPERJOB_SECRET_KEY")
    SUPERJOB_URL = f"{SUPERJOB_DOMEN}/{SUPERJOB_API_VERSION}/{SUPERJOB_API_PATH}/"
    SUPERJOB_HEADERS = {"X-Api-App-Id": SUPERJOB_SECRET_KEY}


class Parser:

    general_job_list: list[dict] = []

    def __init__(
        self,
        city: str,
        job: str,
        date_to: Optional[datetime.date] = datetime.date.today(),
        date_from: Optional[datetime.date] = datetime.date.today()
        - datetime.timedelta(days=10),
    ) -> None:
        self.city = city
        self.job = job
        self.date_to = date_to
        self.date_from = date_from

    async def create_session(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
            data = response.content.decode()
            return data

    async def get_job_from_headhunter(self) -> dict:
        city_from_db = await City.objects.filter(city=self.city).afirst()

        job_list = []
        for page in range(0, 20):

            params = {
                "text": f"NAME:{self.job}",
                "area": city_from_db.hh_id,
                "page": page,
                "per_page": 100,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
            try:
                data = await self.create_session(
                    url=ParserData.HEADHUNTER_URL, params=params
                )
                json_data = orjson.loads(data)
                job_list.append(json_data)
            except httpx.RequestError as exc:
                return f"Адрес {exc.request.url!r} вернул неверный ответ {exc}"

            if (job_list[0]["pages"] - page) <= 1:
                break

        job_dict = {}
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

            datetime_obj = parser.parse(job["published_at"])
            converted_date = datetime.date.strftime(datetime_obj, "%d-%m-%Y")
            job_dict["published_at"] = converted_date

            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта Headhunter завершен")
        return job_dict

    async def get_job_from_superjob(self) -> dict:
        date_from = await self.check_date(self.date_from)
        date_to = await self.check_date(self.date_to)

        job_list = []
        for page in range(0, 5):

            params = {
                "keyword": self.job,
                "town": self.city,
                "page": page,
                "count": 100,
                "date_published_from": date_from,
                "date_published_to": date_to,
            }

            try:
                data = await self.create_session(
                    url=ParserData.SUPERJOB_URL,
                    params=params,
                    headers=ParserData.SUPERJOB_HEADERS,
                )
                json_data = orjson.loads(data)
                job_list.append(json_data)
            except httpx.RequestError as exc:
                return f"Адрес {exc.request.url!r} вернул неверный ответ {exc}"

            if (job_list[0]["total"] - page) <= 1:
                break

        job_dict = {}
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

            timestamp = datetime.datetime.fromtimestamp(job["date_published"])
            converted_date = timestamp.strftime("%d-%m-%Y")
            job_dict["published_at"] = converted_date

            Parser.general_job_list.append(job_dict.copy())

        print("Сбор вакансий с сайта SuperJob завершен")
        return job_dict

    @staticmethod
    async def check_date(date: str) -> datetime:
        if isinstance(date, datetime.date):
            converted_date = datetime.datetime.combine(date, datetime.time()).timestamp()
            return converted_date
        else:
            return date


async def run(city="москва", job="Java"):
    parser = Parser(city=city, job=job)
    task1 = asyncio.create_task(parser.get_job_from_headhunter())
    task2 = asyncio.create_task(parser.get_job_from_superjob())
    await asyncio.gather(task1, task2)

    # print(f"Количество вакансий: {len(Parser.general_job_list)}", Parser.general_job_list)
    return Parser.general_job_list


if __name__ == "__main__":

    async def main():
        await run()

    asyncio.run(main())
