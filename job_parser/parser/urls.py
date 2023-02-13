from django.urls import path
from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("list/", views.VacancyListView.as_view(), name="list"),
    path("favourite/", views.add_to_favourite_view, name="favourite"),
    path("delete-favourite/", views.delete_from_favourite_view, name="delete_favourite"),
    path("add-to-black-list/", views.add_to_black_list_view, name="add_to_black_list"),
]
