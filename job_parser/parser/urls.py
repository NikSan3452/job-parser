from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="home"),
    path("list/", views.VacancyListView.as_view(), name="list"),
    path("favourite/", views.AddVacancyToFavouritesView.as_view(), name="favourite"),
    path(
        "clear-favourite-list/",
        views.ClearVacancyFavouriteList.as_view(),
        name="clear_favourite_list",
    ),
    path(
        "delete-favourite/",
        views.DeleteVacancyFromFavouritesView.as_view(),
        name="delete_favourite",
    ),
    path(
        "add-to-black-list/",
        views.AddVacancyToBlackListView.as_view(),
        name="add_to_black_list",
    ),
    path(
        "clear-blacklist-list/",
        views.ClearVacancyBlackList.as_view(),
        name="clear_blacklist_list",
    ),
    path("hide-company/", views.HideCompanyView.as_view(), name="hide_company"),
    path(
        "clear-hidden-companies-list/",
        views.ClearHiddenCompaniesList.as_view(),
        name="clear_hidden_companies_list",
    ),
    path(
        "delete-from-blacklist/",
        views.DeleteVacancyFromBlacklistView.as_view(),
        name="delete_from_blacklist",
    ),
    path(
        "delete-from-hidden-companies/",
        views.DeleteFromHiddenCompaniesView.as_view(),
        name="delete_from_hidden_companies",
    ),
]
