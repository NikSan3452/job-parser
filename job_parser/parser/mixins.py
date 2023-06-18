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
    def get_vacancies(self, form_data: dict) -> QuerySet:
        params = self.get_request_params(form_data)
        vacancies = self.fetch(params)
        return vacancies

    def get_form_data(self, form: SearchingForm) -> dict:
        """Метод получения данных формы.

        Этот метод принимает объект формы `form` и обрабатывает его асинхронно.
        Внутри метода создается список полей формы для обработки.
        Затем для каждого поля извлекается значение из очищенных данных формы и
        преобразуется при необходимости.
        В конце метода возвращается словарь с данными формы.

        Args:
            form (SearchingForm): Объект формы.

        Returns:
            dict: Словарь с данными формы.
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
        """Метод проверки вакансий в черном списке.

        Этот метод принимает список вакансий `vacancies` и объект запроса `request`,
        и обрабатывает их асинхронно.
        Внутри метода проверяется, является ли пользователь анонимным. Если да, то
        возвращается изначальный список вакансий.
        Затем для пользователя извлекается список URL-адресов из черного списка.
        Далее проверяется наличие URL-адреса вакансии в черном списке и формируется
        отфильтрованный список вакансий.
        Если URL-адрес вакансии был в списке избранных, то он удаляется оттуда.
        В случае ошибки будет вызвано исключение, которое записывается в лог.
        В конце метода возвращается отфильтрованный список вакансий.

        Args:
            vacancies (QuerySet): Список вакансий.
            request (HttpRequest): Объект запроса.

        Returns:
            QuerySet: Отфильтрованный список вакансий.
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
        """Метод проверки компаний в скрытом списке.

        Этот метод принимает список вакансий `vacancies` и объект запроса `request`,
        и обрабатывает их асинхронно.
        Внутри метода проверяется, является ли пользователь анонимным. Если да, то
        возвращается изначальный список вакансий.
        Затем для пользователя извлекается список названий компаний из скрытого списка.
        Далее проверяется наличие названия компании в скрытом списке и формируется
        отфильтрованный список вакансий.
        В случае ошибки будет вызвано исключение, которое записывается в лог.
        В конце метода возвращается отфильтрованный список вакансий.

        Args:
            vacancies (list[dict]): Список вакансий.
            request (HttpRequest): Объект запроса.

        Returns:
            list[dict]: Отфильтрованный список вакансий.
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
        """Метод получения списка избранных вакансий.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода проверяется, является ли пользователь анонимным. Если да, то
        возвращается пустой список.
        Затем извлекается список избранных вакансий для пользователя.
        В случае ошибки будет вызвано исключение, которое записывается в лог.
        В конце метода возвращается список избранных вакансий.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            QuerySet | list: Список избранных вакансий.
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
        title: str = form_data.get("title", None)
        return title.strip() if title else None

    def get_city(self, form_data: dict) -> str | None:
        city: str = form_data.get("city", None)
        return city.lower().strip() if city else None

    def get_date_from(self, form_data: dict) -> str | None:
        date_from: str = form_data.get("date_from", None)
        date_from = utils.check_date_from(date_from)
        return date_from

    def get_date_to(self, form_data: dict) -> str | None:
        date_to: str = form_data.get("date_to", None)
        date_to = utils.check_date_to(date_to)
        return date_to

    def get_experience(self, form_data: dict) -> str | None:
        experience: str = form_data.get("experience", None)
        if experience == ["Не имеет значения"]:
            experience = None
        return experience

    def get_remote(self, form_data: dict) -> bool | None:
        remote: str = form_data.get("remote", None)
        return bool(remote) if remote else None

    def get_job_board(self, form_data: dict) -> str | None:
        job_board = form_data.get("job_board", None)
        if job_board == ["Не имеет значения"]:
            job_board = None
        return job_board

    def get_title_search(self, form_data: dict) -> str | None:
        title_search = form_data.get("title_search", None)
        return bool(title_search) if title_search else None
