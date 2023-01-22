from django.db import models
from profiles.models import Profile


class City(models.Model):
    city_id = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=50, verbose_name="Город", unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.city


class Vacancy(models.Model):
    user = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    url = models.URLField(unique=True)
    title = models.CharField(max_length=250, verbose_name="Вакансия")
    salary_from = models.CharField(max_length=50, null=True, verbose_name="Зарплата от")
    salary_to = models.CharField(max_length=50, null=True, verbose_name="Зарплата до")
    company = models.CharField(max_length=250, verbose_name="Компания")
    description = models.TextField(
        max_length=5000, null=True, verbose_name="Описание вакансии"
    )
    city = models.CharField(max_length=250, verbose_name="Город")
    published_at = models.DateField(auto_now_add=True, verbose_name="Дата публикации")
    favourite = models.BooleanField(default=False, verbose_name="Избраное")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title
