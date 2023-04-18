from django.urls import path
from profiles import views

app_name = "profiles"

urlpatterns = [
    path("profile/<str:username>/", views.ProfileView.as_view(), name="profile"),
    path(
        "profile/<str:username>/delete-from-blacklist/",
        views.delete_from_blacklist_view,
        name="delete_from_blacklist",
    ),
    path(
        "profile/<str:username>/delete-from-hidden-companies/",
        views.delete_from_hidden_companies_view,
        name="delete_from_hidden_companies",
    ),
]
