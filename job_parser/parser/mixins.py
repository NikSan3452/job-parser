import os
import datetime
import pickle
import redis
from typing import Any

from django.contrib import auth, messages
from django.core.paginator import Paginator
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q
from django.conf import settings

from parser.models import City, FavouriteVacancy, VacancyBlackList, VacancyScraper
from parser.forms import SearchingForm
from parser.api.utils import Utils


utils = Utils()


class VacancyHelpersMixin:
    """Класс предоставляет вспомогательные методы"""

    def __init__(self) -> None:
        self.cache_key = None

    async def check_request_data(self, request: Any) -> dict:
        """Проверяет параметры запроса и если они None или False,
        удаляет их из словаря.

        Args:
            request (Any): Запрос.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        request_data = request.GET.dict()

        if request_data.get("city") == "None":
            del request_data["city"]
        if request_data.get("date_from") == "None":
            del request_data["date_from"]
        if request_data.get("date_to") == "None":
            del request_data["date_to"]
        if (
            request_data.get("title_search") == "False"
            or request_data.get("title_search") == "None"
        ):
            del request_data["title_search"]
        if request_data.get("experience") == "None":
            del request_data["experience"]
        if request_data.get("remote") == "False" or request_data.get("remote") == "None":
            del request_data["remote"]
        return request_data

    async def check_vacancy_black_list(self, vacancies: list[dict], request: Any) -> list[dict]:
        """Проверяет добавлена ли вакансия в черный список
        и есла да, то удаляет ее из выдачи и избранного.

        Args:
            vacancies (list[dict]): Список вакансий из API.
            request (Any): Запрос.

        Returns:
            list[dict]: Список вакансий без добавленных в черный список.
        """
        try:
            user = auth.get_user(request)

            for vacancy in vacancies.copy():
                async for job in VacancyBlackList.objects.all():
                    if vacancy.get("url") == job.url:
                        try:
                            FavouriteVacancy.objects.filter(
                                user=user, url=vacancy.get("url")
                            ).delete()
                        except:
                            pass
                        vacancies.remove(vacancy)
            return vacancies
        except Exception as exc:
            print(f"Ошибка базы данных в функции {self.check_vacancy_black_list}: {exc}")

    async def get_favourite_vacancy(self, request: Any):
        """Получает список вакансий добавленных в избранное.

        Args:
            request (Any): Запрос.

        Returns:
            FavouriteVacancy: Список вакансий добавленных в избранное.
        """
        try:
            user = auth.get_user(request)
            if not isinstance(user, AnonymousUser):
                list_favourite = FavouriteVacancy.objects.filter(user=user)
            else:
                list_favourite = []
            return list_favourite
        except Exception as exc:
            print(f"Ошибка базы данных в функции {self.get_favourite_vacancy}: {exc}")

    async def get_pagination(self, request: Any, job_list: list[dict], context: dict) -> None:
        """Добавляет пагинацию.

        Args:
            request (Any): Запрос.
            job_list (list[dict]): Список вакансий.
            context (dict): Контекст.
        """
        paginator = Paginator(job_list, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj

    async def get_form_data(self, form: SearchingForm) -> None:
        """Получает данные из формы.

        Args:
            form (Any): Форма.

        Returns:
            None: None
        """
        city = form.cleaned_data.get("city")
        if city:
            city = city.lower()
        else:
            city = None

        job = form.cleaned_data.get("job")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        title_search = form.cleaned_data.get("title_search")
        experience = int(form.cleaned_data.get("experience"))
        remote = form.cleaned_data.get("remote")
        return city, job, date_from, date_to, title_search, experience, remote

    async def get_city_id(self, city: Any, request: Any) -> str | None:
        """Получет id города из базы данных.
            Данный id необходим для API Headhunter и Zarplata,
            т.к поиск по городам осуществляется по их id.
        Args:
            form (Any): Форма.
            request (Any): Запрос.
        Returns: str | None: id города."""
        city_id = None

        if city:
            try:
                city_from_db = await City.objects.filter(city=city).afirst()
            except Exception as exc:
                print(f"Ошибка базы данных в функции {self.get_city_id.__name__}: {exc}")

            if city_from_db:
                city_id = city_from_db.city_id
            else:
                messages.error(
                    request,
                    """Город с таким названием отсуствует в базе""",
                )
        return city_id


class RedisCacheMixin:
    async def create_cache_key(self, request: Any) -> str:
        """Создает кэш - ключ в виде идетификатора сессии.

        Args:
            request (Any): Запрос.

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
        try:
            result = settings.CACHE.get(self.cache_key)
            if result:
                return pickle.loads(result)
        except Exception as exc:
            print(f"Ошибка в функции {self.get_data_from_cache.__name__}: {exc}")

    async def set_data_to_cache(self, job_list: list[dict]) -> Any:
        """Добавляет данные в кэш.

        Args:
            request (Any): Запрос.
            job_list (list[dict]): Список вакансий.

        Returns:
            Any: Список вакансий.
        """
        try:
            pickle_dump = pickle.dumps(job_list)
            settings.CACHE.set(self.cache_key, pickle_dump, ex=3600)
        except Exception as exc:
            print(f"Ошибка в функции {self.set_data_to_cache.__name__}: {exc}")


class VacancyScraperMixin:
    """Класс содержит методы для получения вакансий из скрапера."""

    async def get_vacancies_from_scraper(
        self,
        city: str | None,
        job: str,
        date_from: datetime.date,
        date_to: datetime.date,
        title_search: bool,
        experience: int,
        remote: bool,
    ) -> VacancyScraper:
        """Получает вакансии из скрапера.

        Args:
            city (str | None): Город.
            job (str): Работа.
            date_from (datetime.date): Дата от.
            date_to (datetime.date): Дата до.
            title_search (bool): Поиск в заголовке вакансии.
            experience (int): Опыт работы.
            remote (bool): Удаленная работа.

        Returns:
            _type_: Список вакансий.
        """
        params: dict = {}  # Словарь параметров запроса

        # Проверяем дату и если нужно устанавливаем дефолтную
        date_from, date_to = utils.check_date(date_from, date_to)

        # Формируем словарь с параметрами запроса
        if city is not None:
            params.update({"city": city.strip()})
        if experience > 0:
            params.update({"experience": experience})
        if remote:
            params.update({"remote": remote})
        params.update({"published_at__gte": date_from})
        params.update({"published_at__lte": date_to})

        if job is not None:
            job = job.lower().strip()

        # Если чекбокс с поиском в заголовке вакансии активен,
        # то поиск осуществляется только по столбцу title
        if title_search:
            job_list_from_scraper = (
                VacancyScraper.objects.filter(title__icontains=job, **params)
                .order_by("-published_at")
                .values()
            )

        # Иначе поиск осуществляется также в описании вакансии
        else:
            job_list_from_scraper = (
                VacancyScraper.objects.filter(
                    Q(title__icontains=job) | Q(description__icontains=job),
                    **params,
                )
                .order_by("-published_at")
                .values()
            )

        return job_list_from_scraper

    async def add_vacancy_to_job_list_from_api(
        self, job_list_from_api: list[dict], job_list_from_scraper: VacancyScraper
    ) -> list[dict]:
        async for job in job_list_from_scraper:
            job_list_from_api.append(job)
        return job_list_from_api
