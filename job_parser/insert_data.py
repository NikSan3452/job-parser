import json
import os
import sys

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"

import django

django.setup()

from parser.models import City


def insert_data():
    with open("city.json") as f:
        data = json.loads(f.read())
        seen = set()
        data = {k: v for k, v in data.items() if v not in seen and not seen.add(v)}
        city_objects = [City(city_id=key, city=value) for key, value in data.items()]
        City.objects.bulk_create(city_objects)
    print("Города успешно занесены в базу данных")


if __name__ == "__main__":

    insert_data()
