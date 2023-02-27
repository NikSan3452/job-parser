import json

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic.edit import FormView
from logger import logger, setup_logging
from parser.api import main
from parser.forms import SearchingForm
from parser.mixins import RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin
from parser.models import FavouriteVacancy, VacancyBlackList

# Логирование
setup_logging()


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
        self.job_list_from_api = await self.get_data_from_cache()

        # Отображаем вакансии, которые в избранном
        list_favourite = await self.get_favourite_vacancy(request)

        context = {
            "form": form,
            "object_list": self.job_list_from_api,
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

        # Проверяем добавлена ли вакансия в черный список
        await self.check_vacancy_black_list(self.job_list_from_api, request)

        # Пагинация
        await self.get_pagination(request, self.job_list_from_api, context)

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
            (
                city,
                job,
                date_from,
                date_to,
                title_search,
                experience,
                remote,
                job_board,
            ) = await self.get_form_data(form)

            # Получаем id города для API HeadHunter и Zarplata
            city_id = await self.get_city_id(city, request)
            try:
                # Если выбранная площадка относится к скраперу - получаем данные только из скрапера
                if job_board in ("Habr career",):
                    job_list_from_scraper = await self.get_vacancies_from_scraper(
                        request,
                        city,
                        job,
                        date_from,
                        date_to,
                        title_search,
                        experience,
                        remote,
                        job_board,
                    )
                    view_logger.debug("Получены вакансии из скрапера")
                else:
                    # Получаем список вакансий из API и скрапера
                    self.job_list_from_api = await main.run(
                        city=city,
                        city_from_db=city_id,
                        job=job,
                        date_from=date_from,
                        date_to=date_to,
                        title_search=title_search,
                        experience=experience,
                        remote=remote,
                        job_board=job_board,
                    )

                    job_list_from_scraper = await self.get_vacancies_from_scraper(
                        request,
                        city,
                        job,
                        date_from,
                        date_to,
                        title_search,
                        experience,
                        remote,
                        job_board,
                    )
                    view_logger.debug("Получены вакансии из API и скрапера")
            except Exception as exc:
                view_logger.exception(exc)

            # Добавляем вакансии из скрапера в список вакансий из api
            await self.add_vacancy_to_job_list_from_api(
                self.job_list_from_api, job_list_from_scraper
            )

            # Сохраняем данные в кэше
            await self.create_cache_key(request)
            await self.set_data_to_cache(self.job_list_from_api)

            # Проверяем добавлена ли вакансия в черный список
            vacancies = await self.check_vacancy_black_list(
                self.job_list_from_api, request
            )

            # Отображаем вакансии, которые в избранном
            list_favourite = await self.get_favourite_vacancy(request)

            context = {
                "city": city,
                "job": job,
                "date_from": date_from,
                "date_to": date_to,
                "title_search": title_search,
                "experience": experience,
                "remote": remote,
                "job_board": job_board,
                "form": form,
                "object_list": vacancies,
                "list_favourite": list_favourite,
            }

            # Пагинация
            await self.get_pagination(request, self.job_list_from_api, context)

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
