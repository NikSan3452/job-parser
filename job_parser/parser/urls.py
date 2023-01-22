from django.urls import path
from . import views 

urlpatterns = [
path('', views.HomePageView.as_view(), name='home'),
path('list/', views.VacancyList.as_view(), name='list'),
]