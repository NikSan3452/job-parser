import json
import os
import sys

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"

import django

django.setup()

from parser.models import City


def insert_data() -> None:
    """
    Функция для вставки данных о городах из файла `city.json` в базу данных.

    Эта функция считывает данные из файла `city.json`, удаляет дубликаты и создает 
    список объектов `City` с данными о городах.
    Затем эти объекты добавляются в базу данных с помощью метода `bulk_create`.
    В конце функции выводится сообщение об успешном добавлении данных в базу данных.

    Returns:
        None
    """
    with open("city.json") as f:
        data = json.loads(f.read())
        seen = set()
        data = {k: v for k, v in data.items() if v not in seen and not seen.add(v)}
        city_objects = [City(city_id=key, city=value) for key, value in data.items()]
        City.objects.bulk_create(city_objects)
    print("Города успешно занесены в базу данных")


if __name__ == "__main__":

    insert_data()
