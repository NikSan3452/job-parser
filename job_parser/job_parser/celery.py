import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_parser.settings")
app = Celery("job_parser")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "sending-vacancy-every-day": {
        "task": "parser.tasks.sending_emails",
        "schedule": crontab(
            hour=settings.SENDING_EMAILS_HOURS, minute=settings.SENDING_EMAILS_MINUTES
        ),
    },
    "run-scraping": {
        "task": "parser.tasks.run_scraper",
        "schedule": crontab(minute=f"*/{settings.SCRAPING_SCHEDULE_MINUTES}"),
    },
    "run-delete-old-vacancies": {
        "task": "parser.tasks.run_delete_old_vacancies",
        "schedule": crontab(
            hour=settings.DELETE_OLD_VACANCIES_HOURS,
            minute=settings.DELETE_OLD_VACANCIES_MINUTES,
        ),
    },
}
