# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import datetime
from parser.models import VacancyScraper
from logger import setup_logging, logger

# Логирование
setup_logging()


class ScraperPipeline:
    def process_item(self, item, spider):
        return item


class HabrPipeline:
    def process_item(self, item, spider):
        """Обрабатывает полученные данные из парсера
        и сохраняет их в базу данных.

        Args:
            item (_type_): Обект содержащий данные.
            spider (_type_): Паук.

        Returns:
            _type_: Обект содержащий данные.
        """
        item_dict = dict(item)
        remote_list = (
            "можно удалённо",
            "можно удаленно",
        )

        item_dict["url"] = item_dict.get("url").lower()
        item_dict["title"] = (
            item_dict.get("title").lower().strip() if item_dict.get("title") else None
        )
        item_dict["description"] = " ".join(
            [word.lower() for word in item_dict.get("description", [])]
        )
        item_dict["city"] = (
            item_dict.get("city").lower() if item_dict.get("city") else None
        )
        item_dict["salary"] = (
            item_dict.get("salary").lower() if item_dict.get("salary") else None
        )
        item_dict["company"] = (
            item_dict.get("company").lower() if item_dict.get("company") else None
        )

        if item_dict.get("experience"):
            experience = item_dict.get("experience").lower()

            if (
                experience == "стажёр (intern)"
                or experience is None
                or experience == ""
            ):
                item_dict["experience"] = "Без опыта"
            elif experience == "младший (junior)":
                item_dict["experience"] = "от 1 до 3 лет"
            elif experience == "средний (middle)":
                item_dict["experience"] = "от 3 до 6 лет"
            elif experience in (
                "старший (senior)",
                "ведущий (lead)",
            ):
                item_dict["experience"] = "от 6 лет"

        if any(
            string.strip().lower() == remote
            for string in item_dict.get("type_of_work", "")
            for remote in remote_list
        ):
            item_dict["remote"] = True

        item_dict["type_of_work"] = ", ".join(
            [word.lower() for word in item_dict.get("type_of_work", "")]
        )

        if item_dict["published_at"] is not None:
            published_at = item_dict.get("published_at").date()

        min_date = datetime.datetime.today() - datetime.timedelta(days=10)
        try:
            if published_at is not None:
                if published_at >= min_date.date():
                    VacancyScraper.objects.get_or_create(**item_dict)
        except Exception as exc:
            logger.exception(exc)

        return item


class GeekjobPipeline:
    def process_item(self, item, spider):
        """Обрабатывает полученные данные из парсера
        и сохраняет их в базу данных.

        Args:
            item (_type_): Обект содержащий данные.
            spider (_type_): Паук.

        Returns:
            _type_: Обект содержащий данные.
        """
        item_dict = dict(item)

        item_dict["url"] = item_dict.get("url").lower()
        item_dict["title"] = (
            item_dict.get("title").lower().strip() if item_dict.get("title") else None
        )
        item_dict["description"] = " ".join(
            [word.lower() for word in item_dict.get("description", [])]
        )
        item_dict["city"] = (
            item_dict.get("city").lower() if item_dict.get("city") else None
        )
        item_dict["salary"] = (
            item_dict.get("salary").lower() if item_dict.get("salary") else None
        )
        item_dict["company"] = (
            item_dict.get("company").lower() if item_dict.get("company") else None
        )

        if item_dict.get("experience"):
            experience = item_dict.get("experience").lower().strip()

            if (
                experience == "опыт работы менее 1 года"
                or experience == "опыт работы любой"
                or experience is None
                or experience == ""
            ):
                item_dict["experience"] = "Без опыта"
            elif experience == "опыт работы от 1 года до 3х лет":
                item_dict["experience"] = "от 1 до 3 лет"
            elif experience == "опыт работы от 3 до 5 лет":
                item_dict["experience"] = "от 3 до 6 лет"
            elif experience == "опыт работы более 5 лет":
                item_dict["experience"] = "от 6 лет"

        if item_dict.get("type_of_work", ""):
            type_of_work = item_dict.get("type_of_work", "")

        if "Удаленная работа" in type_of_work:
            item_dict["remote"] = True

        item_dict["type_of_work"] = item_dict.get("type_of_work", "")

        if item_dict.get("published_at") is not None:
            published_at = self.convert_date(item_dict.get("published_at"))
            item_dict["published_at"] = published_at

        min_date = datetime.datetime.today() - datetime.timedelta(days=10)
        try:
            if published_at is not None:
                if published_at >= min_date.date():
                    VacancyScraper.objects.get_or_create(**item_dict)
        except Exception as exc:
            logger.exception(exc)

        return item

    def convert_date(self, date: str):

        months = {
            "января": "January",
            "февраля": "February",
            "марта": "March",
            "апреля": "April",
            "мая": "May",
            "июня": "June",
            "июля": "July",
            "августа": "August",
            "сентября": "September",
            "октября": "October",
            "ноября": "November",
            "декабря": "December",
        }
        ru_date_str = date.split()
        if ru_date_str[1] in months:
            en_date_str = f"{ru_date_str[0]} {months[ru_date_str[1]]} {datetime.datetime.today().year}"

        date_obj = datetime.datetime.strptime(en_date_str, "%d %B %Y").date()

        return date_obj
