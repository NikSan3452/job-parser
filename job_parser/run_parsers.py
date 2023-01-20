import os
import sys
import asyncio
from datetime import date
from typing import Optional
import parsers

project = os.path.dirname(os.path.abspath("manage.py"))
sys.path.append(project)
os.environ["DJANGO_SETTINGS_MODULE"] = "job_parser.settings"
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django
from parser.models import Vacancy, City
from profiles.models import Profile
from django.contrib.auth.models import User

django.setup()


class SavingVacancies:
    """Класс отвечает за запуск парсера и сохранение
    полученных вакансий в базе данных"""

    def __init__(self) -> None:
        self.db_user: Profile = None
        self.db_city: Profile = None
        self.db_job: Profile = None
        self.db_city_id: City = None

        self.date_from: date = date.today()
        self.date_to: date = date.today()
        self.title_search: bool = False
        self.experience: int = 0

    async def get_profile(self) -> None:
        """Итерирует по профилям пользователей получая их параметры.
        Текущие параметры пользователя передаются
        в функцию парсера - run. На основании этих
        параметров осуществляется поиск вакансий.
        """
        async for item in Profile.objects.all():
            self.db_user = item.pk
            self.db_city = item.city
            self.db_job = item.job
            # Получаем id города из БД по его названию
            # (необходимо для Headhunter и Zarplata.ru)
            self.db_city_id = await City.objects.filter(city=self.db_city).afirst()

    async def get_vacancies(self) -> Optional[list[dict]]:
        """Отвечает за получение вакансий из парсера.

        Returns:
            list[dict]: Список вакансий.
        """
        await self.get_profile()

        vacancies = await parsers.run(
            city=self.db_city,
            city_from_db=self.db_city_id.city_id,
            job=self.db_job,
            date_from=self.date_from,
            date_to=self.date_to,
            title_search=self.title_search,
            experience=self.experience,
        )
        return vacancies

    async def save_vacancies(self) -> None:
        """Отвечает за сохранение полученных вакансий в БД"""
        try:
            vacancies = await self.get_vacancies()

            if len(vacancies) > 0:
                profile = await Profile.objects.aget(user=self.db_user)

                for vacancy in vacancies:
                    await Vacancy.objects.aget_or_create(
                        user=profile,
                        url=vacancy["url"],
                        title=vacancy["title"],
                        salary_from=vacancy["salary_from"],
                        salary_to=vacancy["salary_to"],
                        company=vacancy["company"],
                        description=vacancy["responsibility"],
                        city=vacancy["city"],
                        published_at=vacancy["published_at"],
                    )

        except Exception as exc:
            print(f"Ошибка {exc} Сервер столкнулся с непредвиденной ошибкой")


if __name__ == "__main__":
    saving = SavingVacancies()
    asyncio.run(saving.save_vacancies())
