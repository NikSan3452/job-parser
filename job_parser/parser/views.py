import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from logger import logger, setup_logging
from parser.api import main
from parser.api.utils import Utils
from parser.forms import SearchingForm
from parser.mixins import RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin
from parser.models import FavouriteVacancy, VacancyBlackList

# Логирование
setup_logging()

utils = Utils()


class HomePageView(FormView):
    """Представление домашней страницы."""

    template_name = "parser/home.html"
    form_class = SearchingForm

    def get(self, request):
        super().get(request)
        if not request.session or not request.session.session_key:
            request.session.save()
        return self.render_to_response(self.get_context_data())

    def form_valid(self, form):
        """Валидирует форму домашней страницы.

        Args:
            form: Форма.

        Returns: HTTPResponse
        """
        return super().form_valid(form)


class VacancyListView(View, RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin):
    """Представление страницы со списком ванкасий."""

    form_class = SearchingForm
    template_name = "parser/list.html"
    job_list_from_api: list[dict] = []

    @logger.catch(level="CRITICAL", message="Ошибка в методе <VacancyListView.get()>")
    async def get(self, request, *args, **kwargs):
        """Отвечает за обработку GET запросов к странице со списком вакансий.

        Args:
            request: Запрос.

        Returns: HttpResponse
        """
        # Проверяем параметры запроса перед тем, как передать в форму
        request_data = await self.check_request_data(request)
        form = self.form_class(initial=request_data)

        # Получаем данные из кэша
        await self.create_cache_key(request)
        job_list_from_api = await self.get_data_from_cache()

        # Проверяем добавлена ли вакансия в черный список
        filtered_job_list = await self.check_vacancy_black_list(
            job_list_from_api, request
        )

        # Сортируем вакансии по дате
        sorted_job_list_from_api = await utils.sort_by_date(filtered_job_list)

        # Отображаем вакансии, которые в избранном
        list_favourite = await self.get_favourite_vacancy(request)

        context = {
            "form": form,
            "object_list": sorted_job_list_from_api,
            "list_favourite": list_favourite,
        }

        context["city"] = request_data.get("city")
        context["job"] = request_data.get("job")
        context["date_from"] = request_data.get("date_from")
        context["date_to"] = request_data.get("date_to")
        context["title_search"] = request_data.get("title_search")
        context["experience"] = request_data.get("experience")
        context["remote"] = request_data.get("remote")
        context["job_board"] = request_data.get("job_board")

        # Пагинация
        await self.get_pagination(request, sorted_job_list_from_api, context)

        return render(request, self.template_name, context)

    async def post(self, request, *args, **kwargs):
        """Отвечает за обработку POST запросов к странице со списком вакансий.

        Args:
            request: Запрос.

        Returns: HttpResponse
        """
        form = self.form_class(request.POST)
        view_logger = logger.bind(request=request.POST)

        if form.is_valid():
            # Получаем данные из формы
            params = await self.get_form_data(form)

            # Получаем id города для API HeadHunter и Zarplata
            city_id = await self.get_city_id(params.get("city"), request)
            params.update({"city_from_db": city_id})

            try:
                # Если выбранная площадка относится к скраперу -
                # получаем данные только из скрапера
                if params.get("job_board") in ("Habr career",):
                    self.job_list_from_api.clear()
                    job_list_from_scraper = await self.get_vacancies_from_scraper(
                        request, params
                    )
                    view_logger.debug("Получены вакансии из скрапера")
                else:
                    # А иначе получаем список вакансий сразу из API и скрапера
                    self.job_list_from_api.clear()
                    self.job_list_from_api = await main.run(form_params=params)
                    job_list_from_scraper = await self.get_vacancies_from_scraper(
                        request, params
                    )
                    view_logger.debug("Получены вакансии из API и скрапера")
            except Exception as exc:
                view_logger.exception(exc)

            # Добавляем вакансии из скрапера в список вакансий из api
            shared_job_list = await self.add_vacancy_to_job_list_from_api(
                self.job_list_from_api, job_list_from_scraper
            )

            # Сохраняем данные в кэше
            await self.create_cache_key(request)
            await self.set_data_to_cache(shared_job_list)

            # Проверяем добавлена ли вакансия в черный список
            filtered_shared_job_list = await self.check_vacancy_black_list(
                shared_job_list, request
            )

            # Сортируем список вакансий по дате
            sorted_shared_job_list = await utils.sort_by_date(filtered_shared_job_list)

            # Отображаем вакансии, которые в избранном
            list_favourite = await self.get_favourite_vacancy(request)

            context = {
                "city": params.get("city"),
                "job": params.get("job"),
                "date_from": params.get("date_from"),
                "date_to": params.get("date_to"),
                "title_search": params.get("title_search"),
                "experience": params.get("experience"),
                "remote": params.get("remote"),
                "job_board": params.get("job_board"),
                "form": form,
                "object_list": sorted_shared_job_list,
                "list_favourite": list_favourite,
            }

            # Пагинация
            await self.get_pagination(request, sorted_shared_job_list, context)

        return render(request, self.template_name, context)


@login_required
def add_to_favourite_view(request):
    """Добавляет вакансию в избранное.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    view_logger = logger.bind(request=request.POST)
    if request.method == "POST":

        data = json.load(request)
        vacancy_url = data.get("url")
        vacancy_title = data.get("title")

        try:
            user = auth.get_user(request)
            FavouriteVacancy.objects.get_or_create(
                user=user, url=vacancy_url, title=vacancy_title
            )
            view_logger.info("Вакансия добавлена в избранное")
        except Exception as exc:
            view_logger.exception(exc)
    return JsonResponse({"status": "Вакансия добавлена в избранное"})


@login_required
def delete_from_favourite_view(request):
    """Удаляет вакансию из избранного.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    view_logger = logger.bind(request=request.POST)
    if request.method == "POST":

        data = json.load(request)
        vacancy_url = data.get("url")

        try:
            user = auth.get_user(request)
            FavouriteVacancy.objects.filter(user=user, url=vacancy_url).delete()
            view_logger.info("Вакансия удалена из избранного")
        except Exception as exc:
            view_logger.exception(exc)
    return JsonResponse({"status": "Вакансия удалена из избранного"})


@login_required
def add_to_black_list_view(request):
    """Удаляет вакансию из избранного.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    view_logger = logger.bind(request=request.POST)
    if request.method == "POST":

        data = json.load(request)
        vacancy_url = data.get("url")

        try:
            user = auth.get_user(request)
            VacancyBlackList.objects.get_or_create(user=user, url=vacancy_url)
            view_logger.info("Вакансия добавлена в черный список")
        except Exception as exc:
            view_logger.exception(exc)
    return JsonResponse({"status": "Вакансия добавлена в черный список"})
