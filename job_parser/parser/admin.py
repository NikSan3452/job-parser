from django.contrib import admin

from parser.models import City


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    fields = ("city",)
