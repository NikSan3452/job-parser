import os
import asyncio
import orjson
import datetime
import aiofiles
import httpx
import dataclasses

from typing import Optional
from dotenv import load_dotenv

from models import City

load_dotenv()


@dataclasses.dataclass
class ParserData:
    HEADHUNTER_DOMEN: str = "https://api.hh.ru"
    HEADHUNTER_API_PATH: str = "vacancies"

    SUPERJOB_DOMEN: str = "https://api.superjob.ru"
    SUPERJOB_API_VERSION: str = "2.0"
    SUPERJOB_API_PATH: str = "vacancies"
    SUPERJOB_SECRET_KEY: str = os.getenv("SUPERJOB_SECRET_KEY")


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
            if response.status_code == 200:
                data = response.content.decode()

        return data

    async def get_job_from_headhunter(self) -> list[dict]:
        url = f"{ParserData.HEADHUNTER_DOMEN}/{ParserData.HEADHUNTER_API_PATH}"
        city_from_db = await City.objects.filter(city=self.city).afirst()

        job_list = []
        for page in range(0, 20):
            params = {
                "text": f"NAME:{self.job}",
                "area": city_from_db,
                "page": page,
                "per_page": 100,
                "date_from": self.date_from,
                "date_to": self.date_to,
            }
            data = await self.create_session(url=url, params=params)
            json_data = orjson.loads(data)
            job_list.append(json_data)

        job_dict = {}
        for job in job_list[0]["items"]:
            job_dict['job_board'] = 'HeadHunter'
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
            job_dict["published_at"] = job["published_at"]

            Parser.general_job_list.append(job_dict)

        return Parser.general_job_list

    async def get_job_from_superjob(self) -> str:
        url = f"{ParserData.SUPERJOB_DOMEN}/{ParserData.SUPERJOB_API_VERSION}/{ParserData.SUPERJOB_API_PATH}/"
        headers = {"X-Api-App-Id": ParserData.SUPERJOB_SECRET_KEY}

        self.date_from = await self.check_date(self.date_from)
        self.date_to = await self.check_date(self.date_to)

        for page in range(0, 5):
            params = {
                "keyword": self.job,
                "town": "Москва",
                "page": page,
                "count": 100,
                "date_published_from": self.date_from,
                "date_published_to": self.date_to,
            }
            data = await self.create_session(url=url, params=params, headers=headers)
            json_data = orjson.loads(data)

        return json_data

    @staticmethod
    async def check_date(date: str) -> datetime:
        if not isinstance(date, datetime.datetime):
            if isinstance(date, datetime.date):
                converted_date = datetime.datetime.combine(
                    date, datetime.time()
                ).timestamp()
            else:
                converted_date = datetime.datetime.strptime(
                    date, "%Y-%m-%d"
                ).timestamp()
            return converted_date
        else:
            return date


class HeadHunterParser:
    def __init__(self, area=1, job="Python"):
        self.area = area
        self.job = job
        self.date_to = datetime.date.today()
        self.date_from = self.date_to - datetime.timedelta(days=10)

        self.job_list = []

    async def get_jobs(self, page=0):
        params = {
            "text": f"NAME:{self.job}",  # Текст фильтра
            "area": self.area,  # Город
            "page": page,  # Индекс страницы поиска
            "per_page": 100,  # Кол-во вакансий на 1 странице
            "date_from": self.date_from,  # Дата от
            "date_to": self.date_to,  # Дата до
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url=HEADHUNTER_API_URL, params=params)
            if response.status_code == 200:
                data = response.content.decode()

        return data

    async def read_jobs(self):
        # Считываем первые 2000 вакансий
        for page in range(0, 20):
            data = await self.get_jobs(page)
            json_data = orjson.loads(data)
            self.job_list.append(json_data)

            # Проверка на последнюю страницу, если вакансий меньше 2000
            if (json_data["pages"] - page) <= 1:
                break

        return self.job_list

    async def get_city_list(self):
        url = "https://api.hh.ru/areas"

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url)
            if response.status_code == 200:
                encoded_data = response.content.decode()
                data = orjson.loads(encoded_data)

        cities = {}
        for region in data[0]["areas"]:
            for city in region["areas"]:
                cities[city["id"]] = city["name"].lower()

        async with aiofiles.open("cities.json", "w", encoding="utf-8") as f:
            await f.write(str(cities))
        return cities


class SuperJobParser:
    def __init__(self, city="Москва", job="Python"):
        self.city = city
        self.job = job
        self.period = 7
        self.job_list = []

    async def get_jobs(self):

        params = {
            "keyword": self.job,  # Текст фильтра
            "town": self.city,  # Город
            "period": self.period,
            "count": 100,
        }
        headers = {"X-Api-App-Id": SUPERJOB_SECRET_KEY}

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=SUPERJOB_API_URL, headers=headers, params=params
            )
            if response.status_code == 200:
                data = response.content.decode()

        return data

    async def read_jobs(self):
        data = await self.get_jobs()
        json_data = orjson.loads(data)
        self.job_list.append(json_data)

        for i in range(len(json_data["objects"])):
            print(json_data["objects"][i]["link"])
            print(json_data["objects"][i]["profession"])
            print(json_data["objects"][i]["payment_from"])
            print(json_data["objects"][i]["payment_to"])
            print(json_data["objects"][i]["work"])
            print(json_data["objects"][i]["town"]["title"])
            print(json_data["objects"][i]["date_published"])

        return self.job_list


if __name__ == "__main__":

    async def main():
        parser = Parser(city=1, job="Java", date_from="2023-01-01")
        task3 = asyncio.create_task(parser.get_job_from_headhunter())

        await task3

    asyncio.run(main())
