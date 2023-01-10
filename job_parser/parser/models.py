from django.db import models


class City(models.Model):
    hh_id = models.CharField(max_length=50, unique=True)
    city = models.CharField(max_length=50, verbose_name="Город", unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.city

class Vacancy(models.Model):
    url = models.URLField(unique=True)
    name = models.CharField(max_length=250, verbose_name="Вакансия")
    salary = models.CharField(max_length=50, verbose_name="Зарплата")
    employer = models.CharField(max_length=250, verbose_name="Компания")
    description = models.TextField(max_length=5000, verbose_name="Описание вакансии")
    area = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Город")
    published_at = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-published_at"]

    def __str__(self) -> str:
        return self.name
