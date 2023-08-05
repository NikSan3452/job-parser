from django.contrib.auth.models import User
from django.db import models


class Vacancies(models.Model):
    job_board = job_board = models.CharField(max_length=100, verbose_name="Площадка")
    url = models.URLField(null=False, unique=True)
    title = models.CharField(
        max_length=255,
        db_index=True,
        null=True,
        verbose_name="Вакансия",
    )
    salary_from = models.IntegerField(null=True, blank=True, verbose_name="Зарплата от")
    salary_to = models.IntegerField(null=True, blank=True, verbose_name="Зарплата до")
    salary_currency = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Валюта"
    )
    description = models.TextField(
        max_length=10000, null=True, blank=True, verbose_name="Описание вакансии"
    )
    city = models.TextField(max_length=500, null=True, blank=True, verbose_name="Город")
    company = models.CharField(
        max_length=500, null=True, blank=True, verbose_name="Компания"
    )
    employment = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="Тип занятости"
    )
    schedule = models.CharField(
        max_length=255, null=True, blank=True, verbose_name="График работы"
    )
    experience = models.CharField(
        max_length=100, null=True, blank=True, verbose_name="Опыт работы"
    )
    remote = models.BooleanField(
        default=False, null=True, blank=True, verbose_name="Удаленная компания"
    )
    published_at = models.DateField(
        db_index=True, null=True, blank=True, verbose_name="Дата публикации"
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title


class UserVacancies(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    vacancy = models.ForeignKey(
        Vacancies,
        on_delete=models.CASCADE,
        verbose_name="Вакансия",
        null=True,
        blank=True,
    )
    hidden_company = models.CharField(
        max_length=255, null=True, verbose_name="Компания скрыта"
    )
    is_favourite = models.BooleanField(default=False, verbose_name="В избранном")
    is_blacklist = models.BooleanField(default=False, verbose_name="В черном списке")

    class Meta:
        verbose_name = "Вакансия пользователя"
        verbose_name_plural = "Вакансии пользователя"

    def __str__(self):
        return f"{self.user.username} - {self.vacancy.title if self.vacancy else self.hidden_company}"
