from django.contrib import admin
from profiles.models import Profile


@admin.register(Profile)
class CityAdmin(admin.ModelAdmin):
    fields = ("user", "city", "job")
