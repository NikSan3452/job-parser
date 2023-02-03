import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_parser.settings")
app = Celery("job_parser")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "parsing-job-every-day": {
        "task": "parser.tasks.run_parser",
        "schedule": crontab(hour=12, minute=0),
    },
    "sending-vacancy-every-day": {
        "task": "parser.tasks.sending_emails",
        "schedule": crontab(hour=14, minute=0),
    },
}
