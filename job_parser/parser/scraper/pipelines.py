# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pytz
from dateutil.parser import parse
from itemadapter import ItemAdapter

from parser.models import VacancyScraper


class ScraperPipeline:
    def process_item(self, item, spider):
        return item


class HabrPipeline:
    def process_item(self, item, spider):
        item_dict = dict(item)
        remote_list = ("можно удалённо",)

        item_dict["url"] = item_dict.get("url").lower()
        item_dict["title"] = item_dict.get("title").lower() if item_dict.get("title") else None
        item_dict["description"] = " ".join(
            [word.lower() for word in item_dict.get("description", [])]
        )
        item_dict["city"] = item_dict.get("city").lower() if item_dict.get("city") else None
        item_dict["salary"] = item_dict.get("salary").lower() if item_dict.get("salary") else None
        item_dict["company"] = (
            item_dict.get("company").lower() if item_dict.get("company") else None
        )

        if item_dict.get("experience"):
            experince = item_dict.get("experience").lower()

            if experince in ("стажёр (intern)", "младший (junior)"):
                item_dict["experience"] = "Без опыта"
            elif experince in ("младший (junior)",):
                item_dict["experience"] = "От 1 до 3-х лет"
            elif experince in ("средний (middle)",):
                item_dict["experience"] = "От 3-х до 6 лет"
            elif experince in (
                "старший (senior)",
                "ведущий (lead)",
            ):
                item_dict["experience"] = "Более 6 лет"

        item_dict["type_of_work"] = ", ".join(
            [word.lower() for word in item_dict.get("type_of_work", "")]
        )

        if any(
            string == remote
            for string in item_dict.get("type_of_work", "")
            for remote in remote_list
        ):
            item_dict["remote"] = True

        item_dict["published_at"] = item_dict.get("published_at")

        VacancyScraper.objects.get_or_create(**item_dict)

        return item
