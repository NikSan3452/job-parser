from django.contrib.auth.models import User
from django.db import models


class Vacancies(models.Model):
    job_board = job_board = models.CharField(max_length=100, verbose_name="Площадка")
    url = models.URLField(null=False)
    title = models.CharField(max_length=500, null=True, verbose_name="Вакансия")
    salary_from = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Зарплата от"
    )
    salary_to = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Зарплата до"
    )
    salary_currency = models.CharField(
        max_length=30, null=True, blank=True, verbose_name="Валюта"
    )
    description = models.TextField(
        max_length=10000, null=True, blank=True, verbose_name="Описание вакансии"
    )
    city = models.TextField(
        max_length=5000, null=True, blank=True, verbose_name="Город"
    )
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
    remote = models.BooleanField(default=False, null=True, blank=True)
    published_at = models.DateField(
        null=True, blank=True, verbose_name="Дата публикации"
    )

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title


class Favourite(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    url = models.URLField(null=False, unique=True)
    title = models.CharField(max_length=250, verbose_name="Вакансия")

    class Meta:
        verbose_name = "Избранная вакансия"
        verbose_name_plural = "Избранные вакансии"

    def __str__(self) -> str:
        return self.title


class BlackList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    url = models.URLField(null=False, unique=True)
    title = models.CharField(max_length=250, null=True, verbose_name="Вакансия")

    class Meta:
        verbose_name = "Вакансия в черном списке"
        verbose_name_plural = "Вакансии в черном списке"

    def __str__(self) -> str:
        return self.url


class HiddenCompanies(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    name = models.CharField(max_length=255, verbose_name="Компания")

    class Meta:
        verbose_name = "Скрытая компания"
        verbose_name_plural = "Скрытые компании"

    def __str__(self) -> str:
        return self.name
