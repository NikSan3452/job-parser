import asyncio
import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import Q
from huey import crontab
from huey.contrib.djhuey import periodic_task
from logger import logger, setup_logging
from profiles.models import Profile

from parser.scraping.main import StartScrapers

from .models import Vacancies
from .parsing.main import JobParser

setup_logging()


class EmailSender:
    """Класс для отправки электронных писем с вакансиями."""

    def __init__(self) -> None:
        """
        Инициализация класса.

        Создает пустые списки для хранения профилей и вакансий.
        """
        self.profiles: list[Profile] = []
        self.vacancy_list: list = []

    def get_profiles(self) -> None:
        """
        Получение списка профилей.

        Этот метод получает список профилей из модели `Profile`,
        у которых значение поля `subscribe` равно `True`.
        """
        self.profiles = Profile.objects.filter(subscribe=True)
        logger.debug("Профили получены")

    def get_vacancies(self, profile: Profile) -> None:
        """
        Получение списка вакансий со скрапера.

        Этот метод принимает аргумент `profile` и получает список вакансий
        из модели `VacancyScraper`, у которых значения полей `title`, `city`
        и `published_at` соответствуют значениям этих полей в переданном профиле.

        Args:
            profile: Профиль пользователя.
        """
        self.vacancy_list = Vacancies.objects.filter(
            Q(title__icontains=profile.job) | Q(description__icontains=profile.job),
            city__icontains=profile.city,
            published_at=datetime.date.today(),
        )
        logger.debug("Вакансии со скрапера получены")

    def send_email(self, profile: Profile) -> None:
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

        for vacancy in self.vacancy_list:
            html += f'<h5><a href="{vacancy.url}">{vacancy.title}</a></h5>'
            html += f"<p>{vacancy.company}</p>"
            html += f"<p>Город: {vacancy.city} | Дата публикации: {vacancy.published_at}</p>"

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
        """
        try:
            self.get_profiles()
            for profile in self.profiles:
                self.get_vacancies(profile)
                self.send_email(profile)
        except Exception as exc:
            logger.exception(exc)


@periodic_task(crontab(minute=f"*/{settings.SENDING_EMAILS_HOURS}"))
def start_sending_emails() -> None:
    """
    Отправка электронных писем с вакансиями.

    Эта функция создает экземпляр класса `EmailSender` и вызывает его метод
    `sending_emails` для отправки электронных писем с вакансиями.
    Функция выполняется периодически с интервалом, указанным в настройках.
    """
    sender = EmailSender()
    sender.sending_emails()


@periodic_task(crontab(minute=f"*/{settings.DELETE_OLD_VACANCIES}"))
def delete_old_vacancies() -> None:
    """
    Удаление устаревших вакансий.

    Эта функция удаляет объекты модели `VacancyScraper`, у которых значение поля
    `published_at` меньше или равно текущей дате минус 10 дней.
    Если во время выполнения возникает исключение, оно записывается в журнал.
    Функция выполняется периодически с интервалом, указанным в настройках.
    """
    min_date = datetime.datetime.today() - datetime.timedelta(days=10)
    try:
        Vacancies.objects.filter(published_at__lte=min_date).delete()
    except Exception as exc:
        logger.exception(exc)
    logger.debug("Устаревшие вакансии удалены")


@periodic_task(crontab(minute=f"*/{settings.SCRAPE_HABR}"))
def scrape_habr_task() -> None:
    """
    Запуск скрапера habr.
    """
    parser = StartScrapers()
    asyncio.run(parser.scrape_habr())


@periodic_task(crontab(minute=f"*/{settings.SCRAPE_GEEKJOB}"))
def scrape_geekjob_task() -> None:
    """
    Запуск скрапера geekjob.
    """
    parser = StartScrapers()
    asyncio.run(parser.scrape_geekjob())


@periodic_task(crontab(minute=f"*/{settings.PARSE_HEADHUNTER}"))
def parse_headhunter_task() -> None:
    """
    Запуск парсера headhunter.
    """
    parser = JobParser()
    asyncio.run(parser.parse_headhunter())


@periodic_task(crontab(minute=f"*/{settings.PARSE_ZARPLATA}"))
def parse_zarplata_task() -> None:
    """
    Запуск парсера zarplata.
    """
    parser = JobParser()
    asyncio.run(parser.parse_zarplata())


@periodic_task(crontab(minute=f"*/{settings.PARSE_SUPERJOB}"))
def pars_superjob_task() -> None:
    """
    Запуск парсера superjob.
    """
    parser = JobParser()
    asyncio.run(parser.parse_superjob())


@periodic_task(crontab(minute=f"*/{settings.PARSE_TRUDVSEM}"))
def parse_trudvsem_task() -> None:
    """
    Запуск парсера trudvsem.
    """
    parser = JobParser()
    asyncio.run(parser.parse_trudvsem())
