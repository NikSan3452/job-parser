from dataclasses import dataclass

from loguru import logger
from parser.forms import SearchingForm
from parser.models import Favourite, HiddenCompanies, Vacancies, BlackList
from parser.parsing.utils import Utils
from typing import Any, Awaitable

from django.contrib.auth.mixins import AccessMixin
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.models import AnonymousUser

from logger import setup_logging

# Логирование
setup_logging()

utils = Utils()


@dataclass
class RequestParams:
    """
    Класс для хранения параметров запроса.

    Класс использует декоратор `dataclass` и содержит атрибуты для хранения параметров 
    запроса.

    Attributes:
        title (str): Строка с названием вакансии.
        city (str): Строка с городом.
        date_from (str): Строка с датой начала поиска.
        date_to (str): Строка с датой конца поиска.
        experience (str): Строка с опытом работы.
        job_board (str): Строка с площадкой для поиска.
        remote (str): Строка с флажком удаленной работы.
        title_search (str): Строка с флажком поиска в заголовках вакансий.
    """
    title: str
    city: str
    date_from: str
    date_to: str
    experience: str
    job_board: str
    remote: str
    title_search: str


class AsyncLoginRequiredMixin(AccessMixin):
    """
    Асинхронная версия миксина LoginRequiredMixin Django.

    Этот миксин предназначен для использования в представлениях, доступ к которым
    должен быть разрешен только для аутентифицированных пользователей.
    Если пользователь не аутентифицирован, он будет перенаправлен на страницу входа.

    Наследуется от класса AccessMixin.
    """

    async def dispatch(
        self, request: HttpRequest, *args: Any, **kwargs: Any
    ) -> Awaitable[HttpResponse]:
        """Асинхронный метод dispatch для обработки запросов.

        В этом методе выполняется проверка аутентификации пользователя.
        Если пользователь не аутентифицирован, вызывается метод handle_no_permission,
        который возвращает объект HttpResponseRedirect для перенаправления пользователя
        на страницу входа.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            Awaitable[HttpResponse]: Объект ответа.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        return await super().dispatch(request, *args, **kwargs)


class VacanciesMixin:
    """
    Класс-примесь для работы с вакансиями.

    Класс содержит методы для получения списка вакансий, параметров запроса, 
    данных из формы, проверки черного и скрытого списков и другие вспомогательные 
    методы.
    """
    def get_vacancies(self, form_data: dict) -> QuerySet:
        """
        Метод для получения списка вакансий.

        Метод принимает на вход словарь с данными из формы и возвращает объект 
        класса `QuerySet` с вакансиями. 
        Метод вызывает метод `get_request_params` 
        с передачей ему словаря с данными из формы и получает объект класса 
        `RequestParams` с параметрами запроса. Затем метод вызывает метод `fetch` 
        с передачей ему объекта `RequestParams` и возвращает полученный объект 
        класса `QuerySet`.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            QuerySet: Объект класса `QuerySet` с вакансиями.
        """
        params = self.get_request_params(form_data)
        vacancies = self.fetch(params)
        return vacancies

    def get_form_data(self, form: SearchingForm) -> dict:
        """
        Метод для получения данных из формы.

        Метод принимает на вход объект класса `SearchingForm` и возвращает словарь 
        с данными из формы. 
        Метод проверяет, является ли форма действительной с помощью 
        метода `is_valid`. Если форма действительна, то метод создает список с именами 
        полей формы и проходит по всем элементам списка. Для каждого элемента списка 
        метод получает значение соответствующего поля из атрибута `cleaned_data` 
        объекта `form` и сохраняет его в словарь с данными из формы. В конце работы 
        метода возвращается словарь с данными из формы.

        Args:
            form (SearchingForm): Объект класса `SearchingForm`.

        Returns:
            dict: Словарь с данными из формы.
        """
        form_data: dict = {}
        if form.is_valid():
            fields = [
                "city",
                "title",
                "date_from",
                "date_to",
                "title_search",
                "experience",
                "remote",
                "job_board",
            ]

            for field in fields:
                value = form.cleaned_data.get(field)
                form_data[field] = value

        return form_data

    def get_request_params(self, form_data: dict) -> RequestParams:
        """
        Метод для получения параметров запроса.

        Метод принимает на вход словарь с данными из формы и возвращает объект класса 
        `RequestParams` с параметрами запроса. 
        Метод создает объект класса 
        `RequestParams`, передавая ему значения атрибутов, полученные с помощью методов 
        `get_title`, `get_city`, `get_date_from`, `get_date_to`, `get_experience`, 
        `get_job_board`, `get_remote` и `get_title_search`.
        Полученный объект возвращается как результат работы метода.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            RequestParams: Объект класса `RequestParams` с параметрами запроса.
        """
        params = RequestParams(
            title=self.get_title(form_data),
            city=self.get_city(form_data),
            date_from=self.get_date_from(form_data),
            date_to=self.get_date_to(form_data),
            experience=self.get_experience(form_data),
            job_board=self.get_job_board(form_data),
            remote=self.get_remote(form_data),
            title_search=self.get_title_search(form_data),
        )
        return params

    def fetch(self, params: RequestParams) -> QuerySet:
        """
        Метод для получения списка вакансий.

        Метод принимает на вход объект класса `RequestParams` с параметрами запроса 
        и возвращает объект класса `QuerySet` с вакансиями. 
        Метод создает объект класса 
        `Q` и добавляет к нему условия фильтрации в зависимости от значений атрибутов 
        объекта `params`. Затем вызывает метод `filter` менеджера модели `Vacancies` с 
        передачей ему объекта `Q` и возвращает полученный объект класса `QuerySet`.

        Args:
            params (RequestParams): Объект класса `RequestParams` с параметрами запроса.

        Returns:
            QuerySet: Объект класса `QuerySet` с вакансиями.
        """
        q_objects = Q()

        if params.title:
            if params.title_search:
                q_objects &= Q(title__icontains=params.title)
            else:
                q_objects &= Q(title__icontains=params.title) | Q(
                    description__icontains=params.title
                )

        if params.city:
            q_objects &= Q(city__icontains=params.city)

        if params.date_from:
            q_objects &= Q(published_at__gte=params.date_from)

        if params.date_to:
            q_objects &= Q(published_at__lte=params.date_to)

        if params.experience and params.experience[0] != "Не имеет значения":
            q_objects &= Q(experience__in=params.experience)

        if params.job_board and params.job_board[0] != "Не имеет значения":
            q_objects &= Q(job_board__in=params.job_board)

        if params.remote:
            q_objects &= Q(remote=True)

        vacancies = Vacancies.objects.filter(q_objects)
        return vacancies
    def check_blacklist(
        self, vacancies: QuerySet, request: HttpRequest
    ) -> QuerySet:
        """
        Метод для проверки вакансии в черном списке.

        Метод принимает на вход объект класса `QuerySet` с вакансиями и объект класса 
        `HttpRequest` с запросом и возвращает объект класса `QuerySet` с 
        отфильтрованными вакансиями. 
        Метод получает пользователя из атрибута `user` 
        объекта `request`. Если пользователь является анонимным, то метод возвращает 
        исходный объект класса `QuerySet`. В противном случае метод создает множество 
        с URL-адресами вакансий из черного списка пользователя с помощью менеджера 
        модели `BlackList`. Затем метод создает список с отфильтрованными вакансиями, 
        исключая вакансии с URL-адресами из черного списка. 
        В конце работы метода возвращается список с отфильтрованными вакансиями.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            request (HttpRequest): Объект класса `HttpRequest` с запросом.

        Returns:
            QuerySet: Объект класса `QuerySet` с отфильтрованными вакансиями.
        """
        
        filtered_vacancies: list[dict] = []
        try:
            user = request.user
            # Если пользователь анонимный, то просто возвращаем изначальный список
            if user.is_anonymous:
                return vacancies

            # Получаем url из черного списка
            blacklist_urls = {
                job.url for job in BlackList.objects.filter(user=user)
            }

            # Проверяем наличие url вакансии в черном списке
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.url not in blacklist_urls
            ]

            # Если url вакансии был в списке избранных, то удаляем его от туда
            Favourite.objects.filter(
                user=user, url__in=blacklist_urls
            ).delete()

        except Exception as exc:
            logger.exception(exc)
            filtered_vacancies = vacancies

        return filtered_vacancies

    def check_hidden_list(
        self, vacancies: QuerySet, request: HttpRequest
    ) -> QuerySet:
        """
        Метод для проверки компании в списке скрытых.

        Метод принимает на вход объект класса `QuerySet` с вакансиями и объект класса 
        `HttpRequest` с запросом и возвращает объект класса `QuerySet` с 
        отфильтрованными вакансиями. 
        Метод получает пользователя из атрибута `user` 
        объекта `request`. Если пользователь является анонимным, то метод возвращает 
        исходный объект класса `QuerySet`. В противном случае метод создает множество 
        с названиями компаний из скрытого списка пользователя с помощью менеджера 
        модели `HiddenCompanies`. Затем метод создает список с отфильтрованными 
        вакансиями, исключая вакансии с названиями компаний из скрытого списка. 
        В конце работы метода возвращается список с отфильтрованными вакансиями.

        Args:
            vacancies (QuerySet): Объект класса `QuerySet` с вакансиями.
            request (HttpRequest): Объект класса `HttpRequest` с запросом.

        Returns:
            QuerySet: Объект класса `QuerySet` с отфильтрованными вакансиями.
        """
        mixin_logger = logger.bind(request=request)
        try:
            user = request.user
            # Если пользователь анонимный, то просто возвращаем изначальный список
            if user.is_anonymous:
                return vacancies

            # Получаем компании из списка скрытых
            hidden_companies = {
                company.name
                for company in HiddenCompanies.objects.filter(user=user)
            }

            # Проверяем наличие компании в списке скрытых
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.company not in hidden_companies
            ]

        except Exception as exc:
            mixin_logger.exception(exc)
            filtered_vacancies = vacancies

        return filtered_vacancies

    def get_favourite(self, request: HttpRequest) -> QuerySet | list:
        """
        Метод для получения списка избранных вакансий.

        Метод принимает на вход объект класса `HttpRequest` с запросом и возвращает 
        объект класса `QuerySet` или список с избранными вакансиями. 
        Метод получает пользователя из атрибута `user` объекта `request`. 
        Если пользователь является анонимным, то метод возвращает пустой список. 
        В противном случае вызывает метод `filter` менеджера модели `Favourite` с 
        передачей ему аргумента `user` и возвращает полученный объект класса `QuerySet`.

        Args:
            request (HttpRequest): Объект класса `HttpRequest` с запросом.

        Returns:
            QuerySet | list: Объект класса `QuerySet` или список с избранными вакансиями.
        """
        list_favourite: list = []
        try:
            user = request.user
            if not isinstance(user, AnonymousUser):
                list_favourite = Favourite.objects.filter(user=user).all()
        except Exception as exc:
            logger.exception(exc)
        return list_favourite

    def get_title(self, form_data: dict) -> str | None:
        """
        Метод для получения названия вакансии из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку 
        с названием вакансии или `None`. 
        Метод получает значение ключа "title" из словаря с данными из формы. 
        Если значение равно `None`, то метод возвращает `None`. 
        В противном случае метод удаляет пробельные символы с начала и конца строки 
        и возвращает полученную строку.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с названием вакансии или `None`.
        """
        title: str = form_data.get("title", None)
        return title.strip() if title else None

    def get_city(self, form_data: dict) -> str | None:
        """
        Метод для получения города из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку 
        с городом или `None`. 
        Метод получает значение ключа "city" из словаря с данными из формы. 
        Если значение равно `None`, то метод возвращает `None`. В противном случае 
        метод преобразует строку в нижний регистр, удаляет пробельные символы с начала 
        и конца строки и возвращает полученную строку.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с городом или `None`.
        """
        city: str = form_data.get("city", None)
        return city.lower().strip() if city else None

    def get_date_from(self, form_data: dict) -> str | None:
        """
        Метод для получения даты начала поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с датой 
        начала поиска или `None`. 
        Метод получает значение ключа "date_from" из словаря с данными из формы. 
        Затем метод вызывает функцию `check_date_from` модуля `utils` с передачей ему 
        полученного значения и возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой начала поиска или `None`.
        """
        date_from: str = form_data.get("date_from", None)
        date_from = utils.check_date_from(date_from)
        return date_from

    def get_date_to(self, form_data: dict) -> str | None:
        """
        Метод для получения даты конца поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с датой 
        конца поиска или `None`. 
        Метод получает значение ключа "date_to" из словаря с данными из формы. 
        Затем метод вызывает функцию `check_date_to` модуля `utils` с передачей ему 
        полученного значения и возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с датой конца поиска или `None`.
        """
        date_to: str = form_data.get("date_to", None)
        date_to = utils.check_date_to(date_to)
        return date_to

    def get_experience(self, form_data: dict) -> str | None:
        """
        Метод для получения опыта работы из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с опытом 
        работы или `None`. 
        Метод получает значение ключа "experience" из словаря с данными из формы. 
        Если значение равно списку с одним элементом "Не имеет значения", то метод 
        возвращает `None`. В противном случае метод возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с опытом работы или `None`.
        """
        experience: str = form_data.get("experience", None)
        if experience == ["Не имеет значения"]:
            experience = None
        return experience

    def get_remote(self, form_data: dict) -> bool | None:
        """
        Метод для получения флажка удаленной работы из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает булево значение 
        флажка удаленной работы или `None`. 
        Метод получает значение ключа "remote" из словаря с данными из формы. 
        Если значение равно `None`, то метод возвращает `None`. 
        В противном случае метод преобразует значение в булево и возвращает его.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            bool | None: Булево значение флажка удаленной работы или `None`.
        """
        remote: str = form_data.get("remote", None)
        return bool(remote) if remote else None

    def get_job_board(self, form_data: dict) -> str | None:
        """
        Метод для получения площадки для поиска из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает строку с 
        площадкой для поиска или `None`. 
        Метод получает значение ключа "job_board" из словаря с данными из формы. 
        Если значение равно списку с одним элементом "Не имеет значения", то метод 
        возвращает `None`. В противном случае метод возвращает полученное значение.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            str | None: Строка с площадкой для поиска или `None`.
        """
        job_board = form_data.get("job_board", None)
        if job_board == ["Не имеет значения"]:
            job_board = None
        return job_board

    def get_title_search(self, form_data: dict) -> str | None:
        """
        Метод для получения флажка поиска в заголовках вакансий из данных формы.

        Метод принимает на вход словарь с данными из формы и возвращает булево значение 
        флажка поиска в заголовках вакансий или `None`. Метод получает значение ключа 
        "title_search" из словаря с данными из формы. Если значение равно `None`, 
        то метод возвращает `None`. В противном случае метод преобразует значение 
        в булево и возвращает его.

        Args:
            form_data (dict): Словарь с данными из формы.

        Returns:
            bool | None: Булево значение флажка поиска в заголовках вакансий или `None`.
        """
        title_search = form_data.get("title_search", None)
        return bool(title_search) if title_search else None
