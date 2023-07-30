from django.contrib import admin

from parser.models import UserVacancies, Vacancies


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


@admin.register(UserVacancies)
class UserVacanciesAdmin(admin.ModelAdmin):
    fields = ("user", "url", "title, is_favourite, is_blacklist, hidden_company")
