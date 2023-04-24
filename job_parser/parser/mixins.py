import pickle
from parser.api.utils import Utils
from parser.forms import SearchingForm
from parser.models import (
    City,
    FavouriteVacancy,
    HiddenCompanies,
    VacancyBlackList,
    VacancyScraper,
)
from typing import Any, Awaitable

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator
from django.db.models import Q, QuerySet
from django.http import HttpRequest, HttpResponse
from logger import logger, setup_logging

# Логирование
setup_logging()

utils = Utils()


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


class VacancyHelpersMixin:
    """Класс со вспомогательными методами для работы со списком вакансий.

    Этот класс содержит методы для проверки данных запроса, проверки вакансий и
    компаний в черном и скрытом списках, получения списка избранных вакансий, данных
    пагинации и формы, а также идентификатора города.
    """

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.check_request_data()")
    async def check_request_data(self, request: HttpRequest) -> dict:
        """Метод проверки данных запроса для отображения списка вакансий.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода данные запроса преобразуются в словарь с помощью метода `dict()`.
        Затем удаляются ключи со значениями "None" и "False".
        В случае ошибки будет вызвано исключение, которое записывается в лог.
        В конце метода возвращается обработанный словарь с данными запроса.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            dict: Словарь с данными запроса.
        """
        request_data: dict = request.GET.dict()
        values: tuple = ("None", "False")

        # Т.к во время итерации и удаления ключей размер словаря меняется,
        # чтобы избежать ошибки RuntimeError, оборачиваем список ключей в list,
        # тем самым делаем его копию.
        for key in list(request_data.keys()):
            if request_data.get(key) in values:
                del request_data[key]
        return request_data

    async def check_vacancy_in_black_list(
        self, vacancies: list[dict], request: HttpRequest
    ) -> list[dict]:
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
            vacancies (list[dict]): Список вакансий.
            request (HttpRequest): Объект запроса.

        Returns:
            list[dict]: Отфильтрованный список вакансий.
        """
        mixin_logger = logger.bind(request=request)
        filtered_vacancies: list[dict] = []
        try:
            user = request.user
            # Если пользователь анонимный, то просто возвращаем изначальный список
            if user.is_anonymous:
                return vacancies

            # Получаем url из черного списка
            blacklist_urls = {
                job.url async for job in VacancyBlackList.objects.filter(user=user)
            }

            # Проверяем наличие url вакансии в черном списке
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.get("url") not in blacklist_urls
            ]

            # Если url вакансии был в списке избранных, то удаляем его от туда
            await FavouriteVacancy.objects.filter(
                user=user, url__in=blacklist_urls
            ).adelete()

        except Exception as exc:
            mixin_logger.exception(exc)
            filtered_vacancies = vacancies

        return filtered_vacancies

    async def check_company_in_hidden_list(
        self, vacancies: list[dict], request: HttpRequest
    ) -> list[dict]:
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
                async for company in HiddenCompanies.objects.filter(user=user)
            }

            # Проверяем наличие компании в списке скрытых
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.get("company") not in hidden_companies
            ]

        except Exception as exc:
            mixin_logger.exception(exc)
            filtered_vacancies = vacancies

        return filtered_vacancies

    async def get_favourite_vacancy(self, request: HttpRequest) -> QuerySet | list:
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
        mixin_logger = logger.bind(request=request)
        list_favourite: list = []
        try:
            user = request.user
            if not isinstance(user, AnonymousUser):
                list_favourite = FavouriteVacancy.objects.filter(user=user).all()
        except Exception as exc:
            mixin_logger.exception(exc)
        return list_favourite

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.get_pagination()")
    async def get_pagination(
        self, request: HttpRequest, job_list: list[dict], context: dict
    ) -> None:
        """Метод получения данных пагинации.

        Этот метод принимает объект запроса `request`, список вакансий `job_list` и
        словарь контекста `context`, и обрабатывает их асинхронно.
        Внутри метода создается объект пагинатора с заданным количеством элементов
        на странице.
        Затем извлекается номер страницы из запроса и объект страницы с помощью метода
        `get_page`.
        В контекст добавляются данные объекта страницы и общее количество вакансий.

        Args:
            request (HttpRequest): Объект запроса.
            job_list (list[dict]): Список вакансий.
            context (dict): Словарь контекста.

        Returns:
            None
        """
        paginator = Paginator(job_list, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj
        context["total_vacancies"] = len(job_list)

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.get_form_data()")
    async def get_form_data(self, form: SearchingForm) -> dict:
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
        params: dict = {}
        fields = [
            "city",
            "job",
            "date_from",
            "date_to",
            "title_search",
            "experience",
            "remote",
            "job_board",
        ]

        for field in fields:
            value = form.cleaned_data.get(field)
            if field == "city":
                value = value.lower() if value else None
            elif field == "experience":
                value = int(value)
            params[field] = value

        return params

    async def get_city_id(self, city: str, request: HttpRequest) -> str | None:
        """Метод получения идентификатора города.

        Этот метод принимает название города `city` и объект запроса `request`,
        и обрабатывает их асинхронно.
        Внутри метода проверяется, задано ли название города. Если нет, то возвращается
        `None`.
        Затем пытается извлечь город из базы данных.
        Если город найден в базе данных, то возвращается его идентификатор.
        В противном случае будет вызвано исключение, которое записывается в лог.
        Если город не найден выводится сообщение об ошибке.
        В конце метода возвращается идентификатор города или `None`.

        Args:
            city (str): Название города.
            request (HttpRequest): Объект запроса.

        Returns:
            str | None: Идентификатор города или `None`
        """
        mixin_logger = logger.bind(request=request)
        city_id = None
        city_from_db = None

        if city:  # Если город передан в запросе получаем его id из базы
            try:
                city_from_db = await City.objects.filter(city=city).afirst()
            except Exception as exc:
                mixin_logger.exception(exc)

            if city_from_db:  # Если для города существует id в базе
                city_id = city_from_db.city_id  # то получаем его
            else:  # А иначе выводим сообщение
                messages.error(
                    request,
                    """Город с таким названием отсутствует в базе""",
                )
        return city_id


class RedisCacheMixin:
    """Класс отвечает за взаимодействие с Redis"""

    @logger.catch(message="Ошибка в методе RedisCacheMixin.create_cache_key()")
    async def create_cache_key(self, request: HttpRequest) -> str:
        """
        Метод создает ключ кэша на основе идентификатора сессии из объекта запроса.

        Этот метод принимает объект запроса `request` и асинхронно обрабатывает его.
        Внутри метода извлекается идентификатор сессии из объекта запроса и создается
        ключ кэша, который сохраняется в атрибуте `cache_key` экземпляра класса.
        В конце метода возвращается ключ кэша.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            str: Ключ кэша.
        """
        session_id = request.session.session_key
        self.cache_key = f"session_id:{session_id}"
        return self.cache_key

    async def get_data_from_cache(self) -> Any | None:
        """
        Метод получает данные из кэша с использованием ключа кэша.

        Этот метод асинхронно обрабатывает запрос на получение данных из кэша.
        Внутри метода создается логгер с привязкой к ключу кэша.
        Затем в блоке try/except пытается получить данные из кэша с использованием
        ключа кэша.
        Если данные были найдены, они десериализуются с помощью модуля pickle и
        возвращается результат.
        В противном случае будет вызвано исключение, которое записывается в лог.

        Returns:
            Any | None: Данные из кэша или None, если данные не были найдены.
        """
        mixin_logger = logger.bind(cache_key=self.cache_key)
        try:
            result = settings.CACHE.get(self.cache_key)
            if result:
                return pickle.loads(result)
        except Exception as exc:
            mixin_logger.exception(exc)

    async def set_data_to_cache(self, job_list: list[dict]) -> None:
        """
        Метод сохраняет данные в кэше с использованием ключа кэша и устанавливает время
        истечения срока действия.

        Этот метод принимает список словарей `job_list` и асинхронно обрабатывает его.
        Внутри метода создается логгер с привязкой к ключу кэша.
        Затем в блоке try/except удаляется старый ключ кэша (если он существует),
        сериализуются данные с помощью модуля pickle и сохраняются в кэше с
        использованием ключа кэша и установкой времени истечения срока действия
        в 3600 секунд.
        В случае возникновения исключения оно записывается в лог.

        Args:
            job_list (list[dict]): Список словарей для сохранения в кэше.

        Returns:
            None
        """
        mixin_logger = logger.bind(cache_key=self.cache_key)
        try:
            settings.CACHE.delete(self.cache_key)
            pickle_dump = pickle.dumps(job_list)
            settings.CACHE.set(self.cache_key, pickle_dump, ex=3600)
        except Exception as exc:
            mixin_logger.exception(exc)


class VacancyScraperMixin:
    """Класс содержит методы для получения вакансий из скрапера."""

    async def get_vacancies_from_scraper(
        self, request: HttpRequest, form_params: dict
    ) -> QuerySet:
        """
        Метод получает вакансии из скрапера с использованием параметров формы.

        Этот метод принимает объект запроса `request` и словарь с параметрами формы
        `form_params` и асинхронно обрабатывает их.
        Внутри метода создается логгер с привязкой к данным запроса.
        Затем проверяются даты "от" и "до" с помощью вспомогательного метода
        `check_date`.
        Далее формируется словарь с параметрами запроса на основе данных из формы.
        Если в форме указан город, он добавляется в параметры запроса.
        Если в форме указан опыт работы, он конвертируется с помощью вспомогательного
        метода `convert_experience` и добавляется в параметры запроса.
        Если в форме указано что работа удаленная, она добавляется в параметры запроса.
        Если в форме указана доска объявлений, она добавляется в параметры запроса.
        Даты "от" и "до" также добавляются в параметры запроса.
        Если в форме указана работа, она обрабатывается и используется для поиска
        вакансий в заголовках или в описании (в зависимости от того, выбран ли поиск
        по заголовкам вакансий).
        В случае возникновения ошибок они записываются в лог.
        В конце метода возвращается список найденных вакансий.

        Args:
            request (HttpRequest): Объект запроса.
            form_params (dict): Словарь с параметрами формы.

        Returns:
            QuerySet: Список найденных вакансий.
        """
        mixin_logger = logger.bind(request=request)

        params: dict = {}  # Словарь параметров запроса

        # Проверяем дату и если нужно устанавливаем дефолтную
        date_from, date_to = await utils.check_date(
            form_params.get("date_from"), form_params.get("date_to")
        )

        # Формируем словарь с параметрами запроса
        if form_params.get("city") is not None:
            params.update({"city": form_params.get("city", "").strip()})
        if form_params.get("experience", 0) > 0:
            # Конвертируем опыт
            converted_experience = await utils.convert_experience(
                form_params.get("experience", None), True
            )
            params.update({"experience": converted_experience})
        if form_params.get("remote"):
            params.update({"remote": form_params.get("remote")})
        if form_params.get("job_board") != "Не имеет значения":
            params.update({"job_board": form_params.get("job_board")})
        params.update({"published_at__gte": date_from})
        params.update({"published_at__lte": date_to})

        if form_params.get("job") is not None:
            job = form_params.get("job", "").lower().strip()

        # Если чекбокс с поиском в заголовке вакансии активен,
        # то поиск осуществляется только по столбцу title
        if form_params.get("title_search"):
            try:
                job_list_from_scraper = (
                    VacancyScraper.objects.filter(title__contains=job, **params)
                    .order_by("-published_at")
                    .values()
                )
            except Exception as exc:
                mixin_logger.exception(exc)

        # Иначе поиск осуществляется также в описании вакансии
        else:
            try:
                job_list_from_scraper = (
                    VacancyScraper.objects.filter(
                        Q(title__contains=job) | Q(description__contains=job),
                        **params,
                    )
                    .order_by("-published_at")
                    .values()
                )
            except Exception as exc:
                mixin_logger.exception(exc)
        return job_list_from_scraper

    @logger.catch(
        message="Ошибка в методе VacancyScraperMixin.add_vacancy_to_job_list_from_api()"
    )
    async def add_vacancy_to_job_list_from_api(
        self, job_list_from_api: list[dict], job_list_from_scraper: QuerySet
    ) -> list[dict]:
        """Метод добавляет вакансии из скрапера в список вакансий из API.

        Этот метод принимает список словарей `job_list_from_api` и QuerySet
        `job_list_from_scraper` и асинхронно обрабатывает их.
        Внутри метода создается новый список вакансий из скрапера, который не содержит
        вакансий, уже присутствующих в списке вакансий из API.
        Затем этот новый список добавляется к списку вакансий из API.
        В конце метода возвращается обновленный список вакансий.

        Args:
            job_list_from_api (list[dict]): Список словарей с вакансиями из API.
            job_list_from_scraper (QuerySet): QuerySet с вакансиями из скрапера.

        Returns:
            list[dict]: Обновленный список словарей с вакансиями.
        """
        job_list_from_scraper = [
            job for job in job_list_from_scraper if job not in job_list_from_api
        ]
        job_list_from_api.extend(job_list_from_scraper)
        return job_list_from_api
