import asyncio
import orjson
import datetime
import aiofiles
import httpx


class HeadHunterParser:
    def __init__(self, area=1, job="Python"):
        self.area = area
        self.job = job
        self.date_to = datetime.date.today()
        self.date_from = self.date_to - datetime.timedelta(days=10)

        self.url = "https://api.hh.ru/vacancies"
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
            response = await client.get(url=self.url, params=params)
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


if __name__ == "__main__":

    async def main():
        hh = HeadHunterParser()

        task1 = asyncio.create_task(hh.read_jobs())
        task2 = asyncio.create_task(hh.get_city_list())

        await task1
        await task2

    asyncio.run(main())
