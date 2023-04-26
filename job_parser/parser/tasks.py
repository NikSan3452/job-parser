import asyncio
import datetime
from parser.scraping.run import run

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from huey import crontab
from huey.contrib.djhuey import periodic_task
from logger import logger, setup_logging
from memory_profiler import profile as memory
from profiles.models import Profile

from .api import main
from .models import VacancyScraper

setup_logging()


@memory
@periodic_task(crontab(hour=f"{settings.SENDING_EMAILS_HOURS}"))
def sending_emails() -> None:
    """Отвечает за рассылку электронных писем с вакансиями"""
    try:
        # Выбираем из БД тех пользователей, у которых подключена подписка
        profiles = Profile.objects.filter(subscribe=True)
        logger.debug("Профили получены")
        for profile in profiles:

            # Выбираем из БД вакансии для конкретного пользователя за сегодня
            job_list_from_scraper = VacancyScraper.objects.filter(
                title=profile.job,
                city=profile.city,
                published_at=datetime.date.today(),
            )
            logger.debug("Вакансии со скрапера получены")

            job_list_from_api = asyncio.run(main.run())
            logger.debug("Вакансии с api получены")

            for job in job_list_from_scraper:
                job_list_from_api.append(job)

            # Формируем письмо
            subject = f"Вакансии по вашим предпочтениям за {datetime.date.today()}"
            text_content = "Рассылка вакансий"
            from_email = settings.EMAIL_HOST_USER
            html = ""
            empty = "<h2>К сожалению на сегодня вакансий нет.</h2>"

            # Итерируем по списку вакансий и формируем html документ
            for vacancy in job_list_from_api:
                html += f'<h5><a href="{vacancy.get("url")}">{vacancy.get("title")}</a></h5>'
                html += f'<p>{vacancy.get("company")}</p>'
                html += f'<p>Город: {vacancy.get("city")} | Дата публикации: {vacancy.get("published_at")}</p>'

            # Если вакансий нет, придет сообщение о том, что вакансий на сегодня не 
            # нашлось
            _html = html if html else empty

            to = profile.user.email  # Получаем email из модели User
            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(_html, "text/html")
                msg.send()
                logger.debug(f"Письмо на адрес {to} отправлено")
            except Exception as exc:
                logger.exception(exc)

    except Exception as exc:
        logger.exception(exc)


@memory
@periodic_task(crontab(hour=f"{settings.DELETE_OLD_VACANCIES_HOURS}"))
def delete_old_vacancies(self):
    """Удаляет вакансии старше 10 дней."""
    min_date = datetime.datetime.today() - datetime.timedelta(days=10)
    VacancyScraper.objects.filter(published_at__lte=min_date).delete()


@memory
@periodic_task(crontab(minute=f"*/{settings.SCRAPING_SCHEDULE_MINUTES}"))
def run_parser():
    asyncio.run(run())
