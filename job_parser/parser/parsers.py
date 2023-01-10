import requests
import json
import time
import datetime


class HeadHunterParser:
    def __init__(self, area=1, job="Python"):
        self.area = area
        self.job = job
        self.date_to = datetime.date.today()
        self.date_from = self.date_to - datetime.timedelta(days=3)

        self.url = "https://api.hh.ru/vacancies"
        self.job_list = []

    def get_jobs(self, page=0):
        params = {
            "text": f"NAME:{self.job}",  # Текст фильтра
            "area": self.area,  # Город
            "page": page,  # Индекс страницы поиска
            "per_page": 100,  # Кол-во вакансий на 1 странице
            "date_from": self.date_from,  # Дата от
            "date_to": self.date_to,  # Дата до
        }
        with requests.Session() as session:
            response = session.get(url=self.url, params=params)
            if response.status_code == 200:
                data = response.content.decode()
        return data

    def read_jobs(self):
        # Считываем первые 2000 вакансий
        for page in range(0, 20):
            data = self.get_jobs(page)
            json_data = json.loads(data)
            self.job_list.append(json_data)

            # Проверка на последнюю страницу, если вакансий меньше 2000
            if (json_data["pages"] - page) <= 1:
                break
            time.sleep(0.25)
        return self.job_list

    def get_city_list(self):
        url = "https://api.hh.ru/areas"
        
        with requests.Session() as session:
            response = session.get(url=url)
            if response.status_code == 200:
                data = response.json()

        cities = {}
        for region in data[0]["areas"]:
            for city in region["areas"]:
                cities[city["id"]] = city["name"].lower()

        # with open("cities.json", "w", encoding="utf-8") as f:
        #     f.write(str(cities))
        return cities


if __name__ == "__main__":
    hh = HeadHunterParser()
    hh.read_jobs()
    hh.get_city_list()
