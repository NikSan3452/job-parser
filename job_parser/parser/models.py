from django.db import models

class City(models.Model):
    city = models.CharField(
        max_length=50, verbose_name="Город", unique=True
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

    def __str__(self) -> str:
        return self.city


class Language(models.Model):
    language = models.CharField(
        max_length=50, verbose_name="Язык программирования", unique=True
    )
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Язык программирования"
        verbose_name_plural = "Языки программирования"

    def __str__(self) -> str:
        return self.language


class Vacancy(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=250, verbose_name="Вакансия")
    company = models.CharField(max_length=250, verbose_name="Компания")
    description = models.TextField(max_length=5000, verbose_name="Описание вакансии")
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name="Город"
    )
    language = models.ForeignKey(
        Language, on_delete=models.CASCADE, verbose_name="Язык программирования"
    )
    timestamp = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        ordering = ["-timestamp"]

    def __str__(self) -> str:
        return self.title