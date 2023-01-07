from django.contrib import admin

from parser.models import City, Language, Vacancy


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ("city", "slug")
    prepopulated_fields = {"slug": ("city",)}


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    fields = ("language", "slug")
    prepopulated_fields = {"slug": ("language",)}


@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    fields = ("url", "title", "company", "description", "city", "language")