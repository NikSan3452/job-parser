from django.urls import path

from .views.blacklist import (
    AddToBlackListView,
    ClearBlackList,
    DeleteFromBlacklistView,
)
from .views.favourite import (
    AddToFavouritesView,
    ClearFavouriteList,
    DeleteFromFavouritesView,
)
from .views.hiddenCompanies import (
    ClearHiddenCompaniesList,
    DeleteFromHiddenCompaniesView,
    HideCompanyView,
)
from .views.home import HomePageView
from .views.vacancies import VacancyListView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("vacancies/", VacancyListView.as_view(), name="vacancies"),
    path("favourite/", AddToFavouritesView.as_view(), name="favourite"),
    path(
        "delete-favourite/",
        DeleteFromFavouritesView.as_view(),
        name="delete_favourite",
    ),
    path(
        "clear-favourite-list/",
        ClearFavouriteList.as_view(),
        name="clear_favourite_list",
    ),
    path(
        "add-to-black-list/",
        AddToBlackListView.as_view(),
        name="add_to_black_list",
    ),
    path(
        "delete-from-blacklist/",
        DeleteFromBlacklistView.as_view(),
        name="delete_from_blacklist",
    ),
    path(
        "clear-blacklist-list/",
        ClearBlackList.as_view(),
        name="clear_blacklist_list",
    ),
    path("hide-company/", HideCompanyView.as_view(), name="hide_company"),
    path(
        "delete-from-hidden-companies/",
        DeleteFromHiddenCompaniesView.as_view(),
        name="delete_from_hidden_companies",
    ),
    path(
        "clear-hidden-companies-list/",
        ClearHiddenCompaniesList.as_view(),
        name="clear_hidden_companies_list",
    ),
]
