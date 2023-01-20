from django.contrib import admin

from parser.models import City, Vacancy


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ("city",)
    # prepopulated_fields = {"slug": ("city",)}


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    fields = (
        "user",
        "url",
        "title",
        "salary",
        "company",
        "description",
        "city",
        "published_at",
    )
