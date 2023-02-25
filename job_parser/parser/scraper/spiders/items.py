from scrapy_djangoitem import DjangoItem
from parser import models


class VacancyItem(DjangoItem):
    django_model = models.VacancyScraper
