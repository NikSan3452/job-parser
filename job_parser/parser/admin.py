from django.contrib import admin

from parser.models import (
    City,
    FavouriteVacancy,
    HiddenCompanies,
    VacancyBlackList,
    VacancyScraper,
)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ("city_id", "city")


@admin.register(FavouriteVacancy)
class FavouriteVacancyAdmin(admin.ModelAdmin):
    fields = ("user", "url", "title")


@admin.register(VacancyBlackList)
class VacancyBlackListAdmin(admin.ModelAdmin):
    fields = ("user", "url", "title")


@admin.register(VacancyScraper)
class VacancyScraperAdmin(admin.ModelAdmin):
    fields = (
        "job_board",
        "url",
        "title",
        "description",
        "city",
        "salary",
        "company",
        "experience",
        "type_of_work",
        "remote",
        "published_at",
    )


@admin.register(HiddenCompanies)
class HiddenCompaniesAdmin(admin.ModelAdmin):
    fields = ("user", "name")
