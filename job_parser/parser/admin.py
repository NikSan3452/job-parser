from parser.models import Favourite, HiddenCompanies, Vacancies, BlackList

from django.contrib import admin


@admin.register(Vacancies)
class VacanciesAdmin(admin.ModelAdmin):
    fields = (
        "job_board",
        "url",
        "title",
        "salary_from",
        "salary_to",
        "salary_currency",
        "description",
        "city",
        "company",
        "employment",
        "schedule",
        "experience",
        "remote",
        "published_at",
    )


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    fields = ("user", "url", "title")


@admin.register(BlackList)
class VacancyBlackListAdmin(admin.ModelAdmin):
    fields = ("user", "url", "title")


@admin.register(HiddenCompanies)
class HiddenCompaniesAdmin(admin.ModelAdmin):
    fields = ("user", "name")
