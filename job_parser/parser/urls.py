from django.urls import path
from . import views 

urlpatterns = [
path('', views.homepage, name='home'),
# path('list/', views.list_view, name='list'),
path('list/', views.VacancyList.as_view(), name='list'),
]