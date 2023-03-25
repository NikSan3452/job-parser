import pickle
from typing import Any

from django.contrib import auth, messages
from django.core.paginator import Paginator
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.conf import settings
from django.http import HttpRequest


from parser.models import (
    City,
    FavouriteVacancy,
    VacancyBlackList,
    VacancyScraper,
    HiddenCompanies,
)
from parser.forms import SearchingForm
from parser.api.utils import Utils
from logger import setup_logging, logger

# Логирование
setup_logging()

utils = Utils()


class VacancyHelpersMixin:
    """Класс предоставляет вспомогательные методы"""

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.check_request_data()")
    async def check_request_data(self, request: HttpRequest) -> dict:
        """Проверяет параметры запроса и если они None или False,
        удаляет их из словаря.

        Args:
            request (HttpRequest): Запрос.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        request_data: dict = request.GET.dict()
        values: tuple = ("None", "False")

        # Т.к во время итерации и удаления ключей размер словаря меняется,
        # чтобы исбежать ошибки RuntimeError, оборачиваем список ключей в list,
        # тем самым делаем копию списка ключей.
        for key in list(request_data.keys()):
            if request_data.get(key) in values:
                del request_data[key]
        return request_data

    async def check_vacancy_in_black_list(
        self, vacancies: list[dict], request: HttpRequest
    ) -> list[dict]:
        """Проверяет добавлена ли вакансия в черный список
        и есла да, то удаляет ее из выдачи и избранного.

        Args:
            vacancies (list[dict]): Список вакансий.
            request (HttpRequest): Запрос.

        Returns:
            list[dict]: Список вакансий без добавленных в черный список.
        """
        mixin_logger = logger.bind(request=request)
        try:
            user = auth.get_user(request)
            # Получаем url из черного списка
            blacklist_urls = {job.url async for job in VacancyBlackList.objects.all()}

            # Проверяем наличие url вакансии в черном списке
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.get("url") not in blacklist_urls
            ]

            # Если пользователь анонимный, то просто возвращаем отфильтрованный список
            if user.is_anonymous:
                return filtered_vacancies

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
        """Проверяет скрыта ли вакансия из поисковой выдачи.

        Args:
            vacancies (list[dict]): Список вакансий.
            request (HttpRequest): Запрос.

        Returns:
            list[dict]: Список вакансий без вакансий тех компаний, которые скрыты.
        """
        mixin_logger = logger.bind(request=request)
        try:
            user = auth.get_user(request)
            # Получаем компании из списка скрытых
            hidden_companies = {
                company.name async for company in HiddenCompanies.objects.all()
            }

            # Проверяем наличие компании в списке скрытых
            # и получаем отфильтрованный список
            filtered_vacancies = [
                vacancy
                for vacancy in vacancies
                if vacancy.get("company") not in hidden_companies
            ]

            # Если пользователь анонимный, то просто возвращаем отфильтрованный список
            if user.is_anonymous:
                return filtered_vacancies

        except Exception as exc:
            mixin_logger.exception(exc)
            filtered_vacancies = vacancies

        return filtered_vacancies

    async def get_favourite_vacancy(self, request: HttpRequest):
        """Получает список вакансий добавленных в избранное.

        Args:
            request (HttpRequest): Запрос.

        Returns:
            FavouriteVacancy: Список вакансий добавленных в избранное.
        """
        mixin_logger = logger.bind(request=request)
        try:
            user = auth.get_user(request)
            if not isinstance(user, AnonymousUser):
                list_favourite = FavouriteVacancy.objects.filter(user=user)
            else:
                list_favourite = []
            return list_favourite
        except Exception as exc:
            mixin_logger.exception(exc)

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.get_pagination()")
    async def get_pagination(
        self, request: HttpRequest, job_list: list[dict], context: dict
    ) -> None:
        """Добавляет пагинацию.

        Args:
            request (HttpRequest): Запрос.
            job_list (list[dict]): Список вакансий.
            context (dict): Контекст.
        """
        paginator = Paginator(job_list, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj
        context["total_vacancies"] = len(job_list)

    @logger.catch(message="Ошибка в методе VacancyHelpersMixin.get_form_data()")
    async def get_form_data(self, form: SearchingForm) -> dict:
        """Получает данные из формы.

        Args:
            form (SearchingForm): Форма.

        Returns:
            dict: Словарь со значениями формы.
        """
        params: dict = {}

        city = form.cleaned_data.get("city")
        city = city.lower() if city else None

        params.update({"city": city})
        params.update({"job": form.cleaned_data.get("job")})
        params.update({"date_from": form.cleaned_data.get("date_from")})
        params.update({"date_to": form.cleaned_data.get("date_to")})
        params.update({"title_search": form.cleaned_data.get("title_search")})
        params.update({"experience": int(form.cleaned_data.get("experience"))})
        params.update({"remote": form.cleaned_data.get("remote")})
        params.update({"job_board": form.cleaned_data.get("job_board")})

        return params

    async def get_city_id(
        self, city: SearchingForm, request: HttpRequest
    ) -> str | None:
        """Получет id города из базы данных.
            Данный id необходим для API Headhunter и Zarplata,
            т.к поиск по городам осуществляется по их id.
        Args:
            form (SearchingForm): Форма.
            request (HttpRequest): Запрос.
        Returns: str | None: id города."""
        mixin_logger = logger.bind(request=request)
        city_id = None

        if city:
            try:
                city_from_db = await City.objects.filter(city=city).afirst()
            except Exception as exc:
                mixin_logger.exception(exc)

            if city_from_db:
                city_id = city_from_db.city_id
            else:
                messages.error(
                    request,
                    """Город с таким названием отсуствует в базе""",
                )
        return city_id


class RedisCacheMixin:
    """Класс отвечает за взаимодействие с Redis"""

    @logger.catch(message="Ошибка в методе RedisCacheMixin.create_cache_key()")
    async def create_cache_key(self, request: HttpRequest) -> str:
        """Создает кэш - ключ в виде идетификатора сессии.

        Args:
            request (HttpRequest): Запрос.

        Returns:
            str: Ключ
        """
        session_id = request.session.session_key
        self.cache_key = f"session_id:{session_id}"
        return self.cache_key

    async def get_data_from_cache(self) -> Any:
        """Получает данные из кэша.

        Args:
            request (Any): Запрос.

        Returns:
            Any: Список вакансий.
        """
        mixin_logger = logger.bind(cache_key=self.cache_key)
        try:
            result = settings.CACHE.get(self.cache_key)
            if result:
                return pickle.loads(result)
        except Exception as exc:
            mixin_logger.exception(exc)

    async def set_data_to_cache(self, job_list: list[dict]) -> Any:
        """Добавляет данные в кэш.

        Args:
            request (Any): Запрос.
            job_list (list[dict]): Список вакансий.

        Returns:
            Any: Список вакансий.
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
    ) -> VacancyScraper:
        """Получает вакансии из скрапера.

        Args:
            request (HttpRequest): Запрос.
            form_params (dict): Параметры формы.

        Returns:
            VacancyScraper: Список вакансий.
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
                form_params.get("experience"), True
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
        self, job_list_from_api: list[dict], job_list_from_scraper: VacancyScraper
    ) -> list[dict]:
        """Объединяет списки вакансий из скрапера и API.

        Args:
            job_list_from_api (list[dict]): Список вакансий из API.
            job_list_from_scraper (VacancyScraper): Список вакансий из скрапера.

        Returns:
            list[dict]: Общий список.
        """
        async for job in job_list_from_scraper:
            if job not in job_list_from_api:
                job_list_from_api.append(job)
        return job_list_from_api
