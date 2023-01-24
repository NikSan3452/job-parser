import asyncio
import time
from datetime import date
from typing import Optional

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from .models import Vacancy, City
from profiles.models import Profile
from . import parsers
from job_parser.celery import app


class SavingVacancy:
    """Класс отвечает за запуск парсера и сохранение
    полученных вакансий в базе данных"""

    def __init__(self) -> None:
        self.date_from: date = date.today()
        self.date_to: date = date.today()
        self.title_search: bool = False
        self.experience: int = 0
        self.general_profile_list: list = []

    def get_profile(self) -> list[list]:
        """Итерирует по профилям пользователей получая их параметры.
        Текущие параметры пользователя передаются
        в функцию парсера - run. На основании этих
        параметров осуществляется поиск вакансий.

        Returns:
            list[list]: Список профилей.
        """
        self.general_profile_list.clear()

        try:
            for profile in Profile.objects.all():
                email: str = profile.user.email

                if profile.subscribe:
                    profiles: list = []
                    # Получаем id города из БД по его названию
                    # (необходимо для Headhunter и Zarplata.ru)
                    db_city_id = City.objects.filter(city=profile.city).first()

                    profiles.append(profile)
                    profiles.append(profile.city)
                    profiles.append(db_city_id.city_id)
                    profiles.append(profile.job)
                    profiles.append(email)

                    self.general_profile_list.append(profiles)

            print("Сбор профилей завершен")
            return self.general_profile_list
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")

    def get_vacancies(self) -> Optional[list[dict]]:
        """Отвечает за получение вакансий из парсера
        и запись в базу данных.

        Returns:
            Optional[list[dict]]: Список вакансий.
        """
        try:
            for profile in self.general_profile_list:
                time.sleep(2.5)

                # Получаем вакансии из парсера
                vacancies = asyncio.run(
                    parsers.run(
                        city=profile[1],
                        city_from_db=profile[2],
                        job=profile[3],
                        date_from=self.date_from,
                        date_to=self.date_to,
                        title_search=self.title_search,
                        experience=self.experience,
                    )
                )

                # Записываем в БД вакансии для конкретного профиля
                if len(vacancies) > 0:
                    for vacancy in vacancies:
                        Vacancy.objects.get_or_create(
                            user=profile[0],
                            url=vacancy["url"],
                            title=vacancy["title"],
                            salary_from=vacancy["salary_from"],
                            salary_to=vacancy["salary_to"],
                            company=vacancy["company"],
                            description=vacancy["responsibility"],
                            city=vacancy["city"],
                            published_at=vacancy["published_at"],
                        )
            print("Вакансии получены и записаны в БД")
            return vacancies
        except Exception as exc:
            print(f"Ошибка {exc} Сервер столкнулся с непредвиденной ошибкой")


@app.task
def run_parser():
    """Запуск парсера."""
    saving = SavingVacancy()
    saving.get_profile()
    saving.get_vacancies()


@app.task
def sending_emails() -> None:
    """Отвечает за рассылку электронных писем с вакансиями"""
    
    # Выбираем из БД тех пользователей, у которых покдлючена подписка
    for profile in Profile.objects.filter(subscribe=True):

        # Выбираем из БД вакансии для конкретного пользователя за сегодня
        vacancy_list = Vacancy.objects.filter(published_at=date.today()).filter(
            user=profile
        )

        # Формируем письмо
        subject = f"Вакансии по вашим предпочтениям за {date.today()}"
        text_content = "Рассылка вакансий"
        from_email = settings.EMAIL_HOST_USER
        html = ""
        empty = "<h2>К сожалению на сегодня вакансий нет.</h2>"

        # Итерируем по списку вакансий и формируем html документ
        for vacancy in vacancy_list:
            html += f'<h5><a href="{ vacancy.url }">{ vacancy.title }</a></h5>'
            if vacancy.salary_from:
                html += f"<p>Зарплата от {vacancy.salary_from} "
            if vacancy.salary_to:
                html += f"до {vacancy.salary_to}</p>"
            if vacancy.description:
                html += f"<p>{vacancy.description} </p>"
            html += f"<p>{vacancy.company} </p>"
            html += (
                f"<p>Город: {vacancy.city} | Дата публикации: {vacancy.published_at}</p>"
            )

        # Если вакансий нет, придет сообщение о том, что вакансий на сегодня не нашлось
        _html = html if html else empty

        to = profile.user.email  # Получаем email из модели User
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(_html, "text/html")
            msg.send()
            print(f"Письмо на адрес {to} отправлено")
        except Exception as exc:
            print(f"Ошибка: {exc}. Не удалось отправить письмо")
