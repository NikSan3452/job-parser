from parser.forms import SearchingForm
from parser.mixins import VacanciesMixin
from parser.models import Vacancies

from django.db.models import QuerySet
from django.views.generic import ListView
from logger import setup_logging

# Логирование
setup_logging()


class VacancyListView(ListView, VacanciesMixin):
    """
    Класс для отображения списка вакансий.

    Класс наследуется от классов `ListView` и `VacanciesMixin` и содержит атрибуты 
    и методы для отображения списка вакансий. Класс использует модель `Vacancies` 
    и шаблон "parser/list.html". 

    Attributes:
        model (Model): Модель `Vacancies`.
        template_name (str): Строка с именем шаблона "parser/list.html".
        paginate_by (int): Целое число с количеством элементов на странице.
        vacancies (QuerySet | None): Объект класса `QuerySet` с вакансиями или `None`.

    Methods:
        get_queryset: Метод для получения списка вакансий.
        get_context_data: Метод для получения контекста шаблона.
    """
    model = Vacancies
    template_name = "parser/vacancies.html"
    paginate_by = 5
    vacancies = None

    def get_queryset(self) -> QuerySet:
        """
        Метод для получения списка вакансий.

        Метод возвращает объект класса `QuerySet` с вакансиями. 
        Метод создает объект класса `SearchingForm` с передачей ему атрибута `GET` 
        объекта `request`. 
        Затем вызывает метод `get_form_data` с передачей ему объекта `form` и 
        получает словарь с данными из формы. После чего вызывает метод 
        `get_vacancies` с передачей ему словаря с данными из формы и получает объект 
        класса `QuerySet` с вакансиями. Если пользователь аутентифицирован, то 
        вызывает методы `check_hidden_list` и `check_blacklist` с передачей им объекта 
        класса `QuerySet` с вакансиями и объекта `request` в результате получая 
        отфильтрованный список вакансий. 
        В конце работы метода возвращается объект класса `QuerySet` с вакансиями.

        Returns:
            QuerySet: Объект класса `QuerySet` с вакансиями.
        """
        form = SearchingForm(self.request.GET)
        vacancies = self.get_vacancies(form)
        if self.request.user.is_authenticated:
            hidden_list = self.check_hidden_list(vacancies, self.request)
            filtered_list = self.check_blacklist(hidden_list, self.request)
            vacancies = filtered_list
        return vacancies

    def get_context_data(self, **kwargs) -> dict:
        """
        Метод для получения контекста шаблона.

        Метод принимает на вход произвольное количество именованных аргументов и 
        возвращает словарь с контекстом шаблона. 
        Метод вызывает метод `get_context_data` родительского класса с передачей ему 
        именованных аргументов и получает словарь с контекстом шаблона. Затем метод 
        добавляет в словарь объект класса `SearchingForm` с передачей ему атрибута 
        `GET` объекта `request` и общее количество вакансий из атрибута `count` 
        объекта `paginator`. Если пользователь аутентифицирован, то метод вызывает 
        метод `get_favourite` с передачей ему объекта `request` и добавляет полученный 
        список избранных вакансий в словарь с контекстом шаблона. 
        В конце работы метода возвращается словарь с контекстом шаблона.

        Args:
            **kwargs: Произвольное количество именованных аргументов.

        Returns:
            dict: Словарь с контекстом шаблона.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = SearchingForm(self.request.GET)
        context["total_vacancies"] = context["paginator"].count
        if self.request.user.is_authenticated:
            favourite = self.get_favourite(self.request)
            context["favourite"] = favourite
        return context
