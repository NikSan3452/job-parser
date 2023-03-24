from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    city_id = models.CharField(max_length=255, unique=True)
    city = models.CharField(max_length=255, verbose_name="Город", unique=True)

    class Meta:
        app_label = "parser"
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.city


class VacancyScraper(models.Model):
    job_board = models.CharField(max_length=255, verbose_name="Площадка")
    url = models.URLField(null=False)
    title = models.CharField(max_length=255, null=True, verbose_name="Вакансия")
    description = models.TextField(null=True, verbose_name="Описание вакансии")
    city = models.CharField(max_length=255, null=True, verbose_name="Город")
    salary = models.CharField(max_length=255, null=True, verbose_name="Зарплата")
    company = models.CharField(max_length=255, null=True, verbose_name="Компания")
    experience = models.CharField(max_length=100, null=True, verbose_name="Опыт работы")
    type_of_work = models.CharField(
        max_length=255, null=True, verbose_name="Тип занятости"
    )
    remote = models.BooleanField(
        default=False, null=True, verbose_name="Удаленная работа"
    )
    published_at = models.DateField(null=True, verbose_name="Дата публикации")

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.title


class FavouriteVacancy(models.Model):
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


class VacancyBlackList(models.Model):
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
