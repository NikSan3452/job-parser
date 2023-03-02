import asyncio
from datetime import date

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from profiles.models import Profile

from job_parser.celery import app

from .api import main
from .models import VacancyScraper
from logger import logger, setup_logging

setup_logging()


@app.task
def sending_emails() -> None:
    """Отвечает за рассылку электронных писем с вакансиями"""
    try:
        # Выбираем из БД тех пользователей, у которых покдлючена подписка
        profiles = Profile.objects.filter(subscribe=True)
        logger.debug("Профили получены")
        for profile in profiles:

            # Выбираем из БД вакансии для конкретного пользователя за сегодня
            job_list_from_scraper = VacancyScraper.objects.filter(
                title=profile.job,
                city=profile.city,
                published_at=date.today(),
            )
            logger.debug("Вакансии со скрапера получены")

            job_list_from_api = asyncio.run(main.run())
            logger.debug("Вакансии с api получены")

            for job in job_list_from_scraper:
                job_list_from_api.append(job)

            # Формируем письмо
            subject = f"Вакансии по вашим предпочтениям за {date.today()}"
            text_content = "Рассылка вакансий"
            from_email = settings.EMAIL_HOST_USER
            html = ""
            empty = "<h2>К сожалению на сегодня вакансий нет.</h2>"

            # Итерируем по списку вакансий и формируем html документ
            for vacancy in job_list_from_api:
                html += f'<h5><a href="{vacancy.get("url")}">{vacancy.get("title")}</a></h5>'
                html += f'<p>{vacancy.get("company")}</p>'
                html += f'<p>Город: {vacancy.get("city")} | Дата публикации: {vacancy.get("published_at")}</p>'

            # Если вакансий нет, придет сообщение о том, что вакансий на сегодня не нашлось
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
