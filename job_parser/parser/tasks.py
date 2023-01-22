import asyncio
import time
from datetime import date
from typing import Optional

from .models import Vacancy, City
from profiles.models import Profile
from . import parsers
from job_parser.celery import app


class SavingVacancies:
    """Класс отвечает за запуск парсера и сохранение
    полученных вакансий в базе данных"""

    def __init__(self) -> None:
        self.db_user: Profile = None
        self.date_from: date = date.today()
        self.date_to: date = date.today()
        self.title_search: bool = False
        self.experience: int = 0
        self.profile_list: list = []
        self.general_vacancy_list: list[list[dict]] = []

    def get_profile(self) -> list:
        """Итерирует по профилям пользователей получая их параметры.
        Текущие параметры пользователя передаются
        в функцию парсера - run. На основании этих
        параметров осуществляется поиск вакансий.

        Returns:
            list: Список профилей.
        """
        try:
            for profile in Profile.objects.all():
                self.db_user = profile.pk
                profile_dict: dict = {}
                # Получаем id города из БД по его названию
                # (необходимо для Headhunter и Zarplata.ru)
                db_city_id = City.objects.filter(city=profile.city).first()

                # Формируем словарь со списком профилей
                # Ключ - pk профиля, значение - список параметров профиля
                profile_dict.setdefault(profile.pk, [])
                profile_dict[profile.pk].append(profile.city)
                profile_dict[profile.pk].append(profile.job)
                profile_dict[profile.pk].append(db_city_id.city_id)
                self.profile_list.append(profile_dict)

            print("Сбор профилей завершен")
            return self.profile_list
        except Exception as exc:
            print(f'Ошибка базы данных {exc}')

    def get_vacancies(self) -> Optional[list[dict]]:
        """Отвечает за получение вакансий из парсера.

        Returns:
            Optional[list[dict]]: Список вакансий.
        """
        self.general_vacancy_list.clear()

        try:
            for profile in self.profile_list:
                for item in profile.values():

                    time.sleep(5)
                    
                    vacancies = asyncio.run(
                        parsers.run(
                            city=item[0],
                            city_from_db=item[2],
                            job=item[1],
                            date_from=self.date_from,
                            date_to=self.date_to,
                            title_search=self.title_search,
                            experience=self.experience,
                        )
                    )

                self.general_vacancy_list.append(vacancies)

            print("Вакансии получены")
            return self.general_vacancy_list
        except Exception as exc:
            print(f"Ошибка {exc} Сервер столкнулся с непредвиденной ошибкой")

    def save_vacancies(self) -> None:
        """Отвечает за сохранение полученных вакансий в БД"""
        try:
            if len(self.general_vacancy_list) > 0:
                profile = Profile.objects.get(user=self.db_user)

                for vacancy in self.general_vacancy_list[0]:
                    Vacancy.objects.get_or_create(
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
            print("Вакансии записаны в БД")
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")


@app.task
def main():
    """Запуск."""
    saving = SavingVacancies()
    saving.get_profile()
    saving.get_vacancies()
    saving.save_vacancies()


if __name__ == "__main__":
    main()
