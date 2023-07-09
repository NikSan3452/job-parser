import asyncio
import datetime
from parser.scraping.main import main

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.forms.models import model_to_dict
from huey import crontab
from huey.contrib.djhuey import periodic_task
from logger import logger, setup_logging
from profiles.models import Profile

from .parsing.main import start
from .models import Vacancies

setup_logging()


class EmailSender:
    """
    Класс для отправки электронных писем с вакансиями.

    Этот класс содержит несколько методов для получения профилей,
    вакансий со скрапера и API, объединения списков вакансий и отправки
    электронных писем с вакансиями.
    """

    def __init__(self) -> None:
        """
        Инициализация класса.

        Создает пустые списки для хранения профилей и вакансий.
        """
        self.profiles: list = []
        self.job_list_from_scraper: list = []
        self.job_list_from_api: list = []
        self.shared_job_list: list = []

    def get_profiles(self) -> None:
        """
        Получение списка профилей.

        Этот метод получает список профилей из модели `Profile`,
        у которых значение поля `subscribe` равно `True`.
        """
        self.profiles = Profile.objects.filter(subscribe=True)
        logger.debug("Профили получены")

    def get_jobs_from_scraper(self, profile) -> None:
        """
        Получение списка вакансий со скрапера.

        Этот метод принимает аргумент `profile` и получает список вакансий
        из модели `VacancyScraper`, у которых значения полей `title`, `city`
        и `published_at` соответствуют значениям этих полей в переданном профиле.

        Args:
            profile: Профиль пользователя.
        """
        self.job_list_from_scraper = VacancyScraper.objects.filter(
            title=profile.job,
            city=profile.city,
            published_at=datetime.date.today(),
        )
        logger.debug("Вакансии со скрапера получены")

    def get_jobs_from_api(self, profile) -> None:
        """
        Получение списка вакансий со скрапера.

        Этот метод принимает аргумент `profile` и получает список вакансий
        из модели `VacancyScraper`, у которых значения полей `title`, `city`
        и `published_at` соответствуют значениям этих полей в переданном профиле.

        Args:
            profile: Профиль пользователя.
        """
        params = model_to_dict(profile)
        city_from_db = City.objects.filter(city=profile.city).first()
        params.update(
            date_from=datetime.date.today(),
            date_to=datetime.date.today(),
            city_from_db=city_from_db.city_id,
        )
        self.job_list_from_api = asyncio.run(main.run(params))
        logger.debug("Вакансии с api получены")

    def get_shared_job_list(self) -> None:
        """
        Получение объединенного списка вакансий.

        Этот метод объединяет списки `job_list_from_api` и `job_list_from_scraper`
        в один список `shared_job_list`.
        """
        self.job_list_from_api.extend(self.job_list_from_scraper)
        self.shared_job_list = self.job_list_from_api

    def send_email(self, profile) -> None:
        """
        Отправка электронного письма с вакансиями.

        Этот метод принимает аргумент `profile` и отправляет электронное письмо
        на адрес электронной почты пользователя, указанный в профиле.
        Тема письма и текстовое содержимое формируются из текущей даты и
        настроек. HTML-содержимое формируется из списка `shared_job_list`.
        Если список пуст, вместо него используется сообщение о том,
        что вакансий нет. Для отправки письма используется класс
        `EmailMultiAlternatives` Django.

        Args:
            profile: Профиль пользователя.
        """
        subject = f"Вакансии по вашим предпочтениям за {datetime.date.today()}"
        text_content = "Рассылка вакансий"
        from_email = settings.EMAIL_HOST_USER
        html = ""
        empty = "<h2>К сожалению на сегодня вакансий нет.</h2>"

        for vacancy in self.shared_job_list:
            html += (
                f'<h5><a href="{vacancy.get("url")}">{vacancy.get("title")}</a></h5>'
            )
            html += f'<p>{vacancy.get("company")}</p>'
            html += f'<p>Город: {vacancy.get("city")} | Дата публикации: {vacancy.get("published_at")}</p>'

        _html = html if html else empty

        to = profile.user.email
        try:
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg.attach_alternative(_html, "text/html")
            msg.send()
            logger.debug(f"Письмо на адрес {to} отправлено")
        except Exception as exc:
            logger.exception(exc)

    def sending_emails(self) -> None:
        """
        Отправка электронных писем с вакансиями.

        Этот метод вызывает другие методы этого класса для получения профилей,
        вакансий со скрапера и API, объединения списков вакансий и отправки
        электронных писем с вакансиями. Если во время выполнения возникает
        исключение, оно записывается в журнал.
        """
        try:
            self.get_profiles()
            for profile in self.profiles:
                self.get_jobs_from_scraper(profile)
                self.get_jobs_from_api(profile)
                self.get_shared_job_list()
                self.send_email(profile)
        except Exception as exc:
            logger.exception(exc)




# TODO Раскомментировать
# @periodic_task(crontab(hour=settings.SENDING_EMAILS_HOURS))
# def start_sending_emails() -> None:
#     """
#     Отправка электронных писем с вакансиями.

#     Эта функция создает экземпляр класса `EmailSender` и вызывает его метод
#     `sending_emails` для отправки электронных писем с вакансиями.
#     Функция выполняется периодически с интервалом, указанным в настройках.
#     """
#     sender = EmailSender()
#     sender.sending_emails()


# @periodic_task(crontab(hour=settings.DELETE_OLD_VACANCIES_HOURS))
# def delete_old_vacancies() -> None:
#     """
#     Удаление устаревших вакансий.

#     Эта функция удаляет объекты модели `VacancyScraper`, у которых значение поля
#     `published_at` меньше или равно текущей дате минус 10 дней.
#     Если во время выполнения возникает исключение, оно записывается в журнал.
#     Функция выполняется периодически с интервалом, указанным в настройках.
#     """
#     min_date = datetime.datetime.today() - datetime.timedelta(days=10)
#     try:
#         Vacancies.objects.filter(published_at__lte=min_date).delete()
#     except Exception as exc:
#         logger.exception(exc)
#     logger.debug("Устаревшие вакансии удалены")


@periodic_task(crontab(minute=f"*/{settings.PARSING_SCHEDULE_MINUTES}"))
def run_parsing() -> None:
    """
    Запуск парсера.

    Эта функция запускает асинхронную функцию `start` для выполнения парсинга.
    Функция выполняется периодически с интервалом, указанным в настройках.
    """
    asyncio.run(start())


@periodic_task(crontab(minute=f"*/{settings.SCRAPING_SCHEDULE_MINUTES}"))
def run_scraping() -> None:
    """
    Запуск скрапера.

    Эта функция запускает асинхронную функцию `main` для выполнения скрапинга.
    Функция выполняется периодически с интервалом, указанным в настройках.
    """
    asyncio.run(main())
