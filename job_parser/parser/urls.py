from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("list/", views.VacancyList.as_view(), name="list"),
    path("favourite/", views.add_to_favourite_view, name="favourite"),
    path("delete-favourite/", views.delete_from_favourite_view, name="delete_favourite"),
]
