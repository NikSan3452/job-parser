import os
import pickle
import redis
from typing import Any

from django.contrib import auth, messages
from django.core.paginator import Paginator
from django.contrib.auth.models import AnonymousUser

from parser.models import City, FavouriteVacancy, VacancyBlackList

from dotenv import load_dotenv

load_dotenv()

cache = redis.Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)


class VacancyHelpersMixin:
    """Класс предоставляет вспомогательные методы"""

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
        if request_data.get("title_search") == "False" or request_data.get("title_search") == 'None':
            del request_data["title_search"]
        if request_data.get("experience") == "None":
            del request_data["experience"]
        if request_data.get("remote") == "False" or request_data.get("remote") == 'None':
            del request_data["remote"]
        return request_data

    async def check_vacancy_black_list(
        self, vacancies: list[dict], request: Any
    ) -> list[dict]:
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

    async def get_pagination(
        self, request: Any, job_list: list[dict], context: dict
    ) -> None:
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

    async def get_form_data(self, form: Any) -> None:
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

    async def get_data_from_cache(self, request: Any) -> Any:
        """Получает данные из кэша.

        Args:
            request (Any): Запрос.

        Returns:
            Any: Список вакансий.
        """
        cache_key = await self.create_cache_key(request)
        try:
            result = cache.get(cache_key)
            if result:
                return pickle.loads(result)
        except Exception as exc:
            print(f"Ошибка в функции {self.get_data_from_cache.__name__}: {exc}")

    async def set_data_to_cache(self, request: Any, job_list: list[dict]) -> Any:
        """Добавляет данные в кэш.

        Args:
            request (Any): Запрос.
            job_list (list[dict]): Список вакансий.

        Returns:
            Any: Список вакансий.
        """
        cache_key = await self.create_cache_key(request)
        try:
            pickle_dump = pickle.dumps(job_list)
            cache.set(cache_key, pickle_dump, ex=3600)
        except Exception as exc:
            print(f"Ошибка в функции {self.set_data_to_cache.__name__}: {exc}")

    async def create_cache_key(self, request: Any) -> str:
        """Создает кэш - ключ в виде идетификатора сессии.

        Args:
            request (Any): Запрос.

        Returns:
            str: Ключ
        """
        session_id = request.session.session_key
        cache_key = f"session_id:{session_id}"
        return cache_key
