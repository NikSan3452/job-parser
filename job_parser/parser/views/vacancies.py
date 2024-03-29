from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest
from django.views.generic import ListView
from logger import setup_logging

from parser.forms import SearchingForm
from parser.mixins import VacanciesMixin
from parser.models import Vacancies

# Логирование
setup_logging()


class VacancyListView(ListView, VacanciesMixin):
    model = Vacancies
    template_name = "parser/vacancies.html"
    paginate_by = 5

    async def get(self, request: HttpRequest, *args, **kwargs) -> Any:
        """
        Метод обработки GET-запросов.

        Args:
            request (HttpRequest): Запрос.

        Returns:
            Any: Шаблон с контекстом.
        """
        self.object_list = await self.get_queryset()
        context = await self.get_context_data()
        return self.render_to_response(context)

    async def get_queryset(self) -> QuerySet:
        """
        Метод для получения списка вакансий.

        Returns:
            QuerySet: Объект класса `QuerySet` с вакансиями.
        """
        form = SearchingForm(self.request.GET)
        vacancies = await self.get_vacancies(form)
        if self.request.user.is_authenticated:
            self.filtered_list, self.favourite = self.check_vacancies(
                vacancies, self.request
            )
            vacancies = self.filtered_list
        return vacancies

    async def get_context_data(self, **kwargs) -> dict:
        """
        Метод для получения контекста шаблона.

        Args:
            **kwargs: Произвольное количество именованных аргументов.

        Returns:
            dict: Словарь с контекстом шаблона.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = SearchingForm(self.request.GET)
        context["total_vacancies"] = context["paginator"].count
        if self.request.user.is_authenticated:
            context["favourite"] = self.favourite
        return context
