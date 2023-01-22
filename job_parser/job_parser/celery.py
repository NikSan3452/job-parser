import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "job_parser.settings")
app = Celery("job_parser")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    "parsing-job-every-day": {
        "task": "parser.tasks.main",
        "schedule": crontab(minute="*/1"),
    }
}
