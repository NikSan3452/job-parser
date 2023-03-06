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
        self.item_dict = dict(item)
        self.remote_list = (
            "можно удалённо",
            "можно удаленно",
        )

        self.get_url()
        self.get_title()
        self.get_description()
        self.get_city()
        self.get_salary()
        self.get_company()
        self.get_experience()
        self.get_remote()
        self.get_type_of_work()
        published_at = self.get_published_at()

        min_date = datetime.datetime.today() - datetime.timedelta(days=10)
        try:
            if published_at is not None:
                if published_at >= min_date.date():
                    VacancyScraper.objects.get_or_create(**self.item_dict)
        except Exception as exc:
            logger.exception(exc)

        return item

    def get_url(self):
        """Получет URL вакансии."""
        if self.item_dict.get("url"):
            self.item_dict["url"] = self.item_dict.get("url").lower()

    def get_title(self):
        """Получает название вакансии."""
        if self.item_dict.get("title"):
            self.item_dict["title"] = self.item_dict.get("title").lower().strip()

    def get_description(self):
        """Получает описание вакансии."""
        if self.item_dict.get("description"):
            self.item_dict["description"] = " ".join(
                [word.lower() for word in self.item_dict.get("description", [])]
            )

    def get_city(self):
        """Получает город вакансии."""
        if self.item_dict.get("city"):
            self.item_dict["city"] = self.item_dict.get("city").lower().strip()

    def get_salary(self):
        """Получает зарплату."""
        if self.item_dict.get("salary"):
            self.item_dict["salary"] = self.item_dict.get("salary").lower().strip()

    def get_company(self):
        """Получает название компании разместившей вакансию."""
        if self.item_dict.get("company"):
            self.item_dict["company"] = self.item_dict.get("company").lower().strip()

    def get_experience(self):
        """Получает требуемый опыт."""
        if self.item_dict.get("experience"):
            experience = self.item_dict.get("experience").lower()

            if (
                experience == "стажёр (intern)"
                or experience is None
                or experience == ""
            ):
                self.item_dict["experience"] = "Без опыта"
            elif experience == "младший (junior)":
                self.item_dict["experience"] = "от 1 до 3 лет"
            elif experience == "средний (middle)":
                self.item_dict["experience"] = "от 3 до 6 лет"
            elif experience in (
                "старший (senior)",
                "ведущий (lead)",
            ):
                self.item_dict["experience"] = "от 6 лет"

    def get_remote(self):
        """Проверяет является ли вакансия удаленной работой."""
        if any(
            string.strip().lower() == remote
            for string in self.item_dict.get("type_of_work", "")
            for remote in self.remote_list
        ):
            self.item_dict["remote"] = True

    def get_type_of_work(self):
        """Получает тип занятости."""
        if self.item_dict.get("type_of_work"):
            self.item_dict["type_of_work"] = ", ".join(
                [word.lower() for word in self.item_dict.get("type_of_work", "")]
            )

    def get_published_at(self):
        """Получает дату публикации вакансии.

        Returns:
            _type_: Дата.
        """
        if self.item_dict.get("published_at"):
            published_at = self.item_dict.get("published_at").date()
            self.item_dict["published_at"] = published_at
        return published_at


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
        self.item_dict = dict(item)

        self.get_url()
        self.get_title()
        self.get_description()
        self.get_city()
        self.get_salary()
        self.get_company()
        self.get_experience()
        self.get_type_of_work()
        self.get_remote()
        published_at = self.get_published_at()

        min_date = datetime.datetime.today() - datetime.timedelta(days=10)
        try:
            if published_at is not None:
                if published_at >= min_date.date():
                    VacancyScraper.objects.get_or_create(**self.item_dict)
        except Exception as exc:
            logger.exception(exc)

        return item

    def get_url(self):
        """Получет URL вакансии."""
        if self.item_dict.get("url"):
            self.item_dict["url"] = self.item_dict.get("url").lower()

    def get_title(self):
        """Получает название вакансии."""
        if self.item_dict.get("title"):
            self.item_dict["title"] = self.item_dict.get("title").lower().strip()

    def get_description(self):
        """Получает описание вакансии."""
        if self.item_dict.get("description"):
            self.item_dict["description"] = " ".join(
                [word.lower() for word in self.item_dict.get("description", [])]
            )

    def get_city(self):
        """Получает город вакансии."""
        if self.item_dict.get("city"):
            self.item_dict["city"] = self.item_dict.get("city").lower().strip()

    def get_salary(self):
        """Получает зарплату."""
        if self.item_dict.get("salary"):
            self.item_dict["salary"] = self.item_dict.get("salary").lower().strip()

    def get_company(self):
        """Получает название компании разместившей вакансию."""
        if self.item_dict.get("company"):
            self.item_dict["company"] = self.item_dict.get("company").lower().strip()

    def get_experience(self):
        """Получает требуемый опыт."""
        if self.item_dict.get("experience"):
            self.jobinfo = [word.lower() for word in self.item_dict.get("experience")]
            for string in self.jobinfo:
                if "опыт" in string:
                    experience = string.strip()

            if (
                experience == "опыт работы менее 1 года"
                or experience == "опыт работы любой"
                or experience is None
                or experience == ""
            ):
                self.item_dict["experience"] = "Без опыта"
            elif experience == "опыт работы от 1 года до 3х лет":
                self.item_dict["experience"] = "от 1 до 3 лет"
            elif experience == "опыт работы от 3 до 5 лет":
                self.item_dict["experience"] = "от 3 до 6 лет"
            elif experience == "опыт работы более 5 лет":
                self.item_dict["experience"] = "от 6 лет"

    def get_type_of_work(self):
        """Получает тип занятости."""
        type_work_list = []
        for string in self.jobinfo:
            if "опыт" not in string:
                type_work_list.append(string)

        self.type_of_work = ", ".join(type_work_list)
        self.item_dict["type_of_work"] = self.type_of_work

    def get_remote(self):
        """Проверяет является ли вакансия удаленной работой."""
        if "удаленная" in self.type_of_work:
            self.item_dict["remote"] = True

    def get_published_at(self):
        """Получает дату публикации вакансии.

        Returns:
            _type_: Дата.
        """
        if self.item_dict.get("published_at"):
            published_at = self.convert_date(self.item_dict.get("published_at"))
            self.item_dict["published_at"] = published_at
        return published_at

    def convert_date(self, date: str):
        """Конвертирует полученное значение даты.

        Args:
            date (str): Дата.

        Returns:
            _type_: Дата в виде объекта datetime.
        """
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
        ru_date_str = date.strip().split()
        if ru_date_str[1] in months:
            if len(ru_date_str) >= 3:
                en_date_str = (
                    f"{ru_date_str[0]} {months[ru_date_str[1]]} {ru_date_str[2]}"
                )
            else:
                en_date_str = f"{ru_date_str[0]} {months[ru_date_str[1]]} {datetime.datetime.today().year}"

        date_obj = datetime.datetime.strptime(en_date_str, "%d %B %Y").date()

        return date_obj
