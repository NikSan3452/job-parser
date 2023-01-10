import os
import sys
import asyncio
from django.db import DatabaseError

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"

import django

django.setup()

from parser.models import City, Vacancy
from parser.parsers import HeadHunterParser

hh = HeadHunterParser()

async def add_cities():
    city_list = hh.get_city_list()
    for hh_id, city in city_list.items():
        try:
            await City.objects.acreate(hh_id=hh_id, city=city)
        except DatabaseError:
            pass

asyncio.run(add_cities())