import json
from parser.api import main
from parser.api.utils import Utils
from parser.forms import SearchingForm
from parser.mixins import RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.template.response import TemplateResponse
from django.views import View
from django.views.generic.edit import FormView
from logger import logger, setup_logging

# Логирование
setup_logging()

utils = Utils()


class HomePageView(FormView):
    """Класс представления домашней страницы.

    Этот класс наследуется от `FormView` и используется для отображения домашней
    страницы приложения.

    Args:
        FormView (FormView): Представление для отображения формы и рендеринга ответа шаблона.

    Attributes:
        template_name (str): Имя шаблона для отображения страницы.
        form_class (type): Класс формы для обработки данных.
        success_url (str): URL-адрес для перенаправления после успешной отправки формы.
    """

    template_name: str = "parser/home.html"
    form_class: SearchingForm = SearchingForm
    success_url: str = "/list/"

    def get(self, request: HttpRequest) -> HttpResponse:
        """Метод обработки GET-запроса.

        Этот метод принимает объект запроса `request` и обрабатывает его. 
        Если в сессии пользователя нет ключа сессии, то он сохраняется. 
        Затем получается контекст и отображается страница с использованием этого контекста.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            HttpResponse: Ответ с отображением страницы
        """
        super().get(request)
        if not request.session or not request.session.session_key:
            request.session.save()
        context = self.get_context_data()
        return self.render_to_response(context)

    def form_valid(self, form) -> HttpResponseRedirect:
        """Метод обработки валидной формы.

        Этот метод вызывается, когда форма прошла валидацию. 
        Он перенаправляет пользователя на URL-адрес, указанный в атрибуте `success_url`.

        Args:
            form (Form): Объект формы

        Returns:
            HttpResponseRedirect: Ответ с перенаправлением на другую страницу
        """
        return super().form_valid(form)


class VacancyListView(View, RedisCacheMixin, VacancyHelpersMixin, VacancyScraperMixin):
    """Представление страницы со списком вакансий."""

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
        job_list_from_cache = await self.get_data_from_cache()

        list_favourite = []

        if request.user.is_authenticated:
            # Проверяем находится ли компания в списке скрытых
            job_from_hidden_companies = await self.check_company_in_hidden_list(
                job_list_from_cache, request
            )

            # Проверяем добавлена ли вакансия в черный список
            filtered_job_list = await self.check_vacancy_in_black_list(
                job_from_hidden_companies, request
            )

            # Отображаем вакансии, которые в избранном
            list_favourite = await self.get_favourite_vacancy(request)
            job_list_from_cache = filtered_job_list

        # Сортируем вакансии по дате
        sorted_job_list = await utils.sort_by_date(job_list_from_cache)

        context = {
            "form": form,
            "object_list": sorted_job_list,
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
        await self.get_pagination(request, sorted_job_list, context)

        return TemplateResponse(request, self.template_name, context)

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

            job_list_from_scraper = []
            try:
                # Если выбранная площадка относится к скраперу -
                # получаем данные только из скрапера
                if params.get("job_board") in ("Habr career", "Geekjob"):
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

            list_favourite = []

            if request.user.is_authenticated:
                # Проверяем находится ли компания в списке скрытых
                job_from_hidden_companies = await self.check_company_in_hidden_list(
                    shared_job_list, request
                )

                # Проверяем добавлена ли вакансия в черный список
                filtered_shared_job_list = await self.check_vacancy_in_black_list(
                    job_from_hidden_companies, request
                )

                # Отображаем вакансии, которые в избранном
                list_favourite = await self.get_favourite_vacancy(request)

                shared_job_list = filtered_shared_job_list

            # Сортируем список вакансий по дате
            sorted_shared_job_list = await utils.sort_by_date(shared_job_list)

            # Сохраняем данные в кэше
            await self.create_cache_key(request)
            await self.set_data_to_cache(sorted_shared_job_list)

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

        return TemplateResponse(request, self.template_name, context)


class AddVacancyToFavouritesView(LoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в избранное.

    Этот класс наследуется от LoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в избранное.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса загружаются в переменную `data`, из которой извлекается URL
        и название вакансии.
        Затем пытается получить текущего пользователя и создать
        или получить объект `FavouriteVacancy` с указанными данными пользователя,
        URL и названием вакансии.
        Если все прошло успешно, в лог записывается информация об успешном добавлении
        вакансии в избранное.
        В случае возникновения исключения, оно записывается в лог.
        В конце метода возвращается JSON-ответ с информацией об успешном добавлении
        вакансии в избранное.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешном добавлении вакансии в избранное
        """
        view_logger = logger.bind(request=request.POST)

        data = json.load(request)
        vacancy_url = data.get("url")
        vacancy_title = data.get("title")

        try:
            await FavouriteVacancy.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            view_logger.info(f"Вакансия {vacancy_title} добавлена в избранное")
        except Exception as exc:
            view_logger.exception(exc)
        return JsonResponse(
            {"status": f"Вакансия {vacancy_title} добавлена в избранное"}
        )


class DeleteVacancyFromFavouritesView(LoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из списка избранных.

    Этот класс наследуется от LoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление вакансии из избранного.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса загружаются в переменную `data`, из которой
        извлекается URL вакансии.
        Затем пытается получить текущего пользователя и удалить объект
        `FavouriteVacancy` с указанными данными пользователя и URL вакансии.
        Если все прошло успешно, в лог записывается информация об успешном
        удалении вакансии из избранного.
        В случае возникновения исключения, оно записывается в лог.
        В конце метода возвращается JSON-ответ с информацией об успешном
        удалении вакансии из избранного.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном
            удалении вакансии из избранного
        """
        view_logger = logger.bind(request=request.POST)

        data = json.load(request)
        vacancy_url = data.get("url")
        try:
            await FavouriteVacancy.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} удалена из избранного")
        except Exception as exc:
            view_logger.exception(exc)
        return JsonResponse({"status": f"Вакансия {vacancy_url} удалена из избранного"})


class AddVacancyToBlackListView(LoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в черный список.

    Этот класс наследуется от LoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на добавление вакансии в черный список.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса загружаются в переменную `data`, из которой
        извлекается URL и название вакансии.
        Затем пытается получить текущего пользователя и создать объект
        `VacancyBlackList` с указанными данными пользователя, URL и названием вакансии.
        Также удаляется объект `FavouriteVacancy` с указанными данными пользователя
        и URL вакансии.
        Если все прошло успешно, в лог записывается информация о том, что
        вакансия была добавлена в черный список.
        В случае возникновения исключения, оно записывается в лог.
        В конце метода возвращается JSON-ответ с информацией о том, что
        вакансия была добавлена в черный список.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            JsonResponse: JSON-ответ с информацией о том, что
            вакансия была добавлена в черный список
        """
        view_logger = logger.bind(request=request.POST)

        data = json.load(request)
        vacancy_url = data.get("url")
        vacancy_title = data.get("title")
        try:
            await VacancyBlackList.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            await FavouriteVacancy.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} добавлена в черный список")
        except Exception as exc:
            view_logger.exception(exc)
        return JsonResponse(
            {"status": f"Вакансия {vacancy_url} добавлена в черный список"}
        )


class HideCompanyView(LoginRequiredMixin, View):
    """
    Класс представления для скрытия всех вакансий выбранной компании.

    Этот класс наследуется от LoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на скрытие вакансий выбранной компании.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса загружаются в переменную `data`, из которой извлекается
        имя компании.
        Затем пытается получить текущего пользователя и создать или получить
        объект `HiddenCompanies` с указанными данными пользователя и именем компании.
        Если все прошло успешно, в лог записывается информация о том, что компания
        была успешно скрыта.
        В случае возникновения исключения, оно записывается в лог.
        В конце метода возвращается JSON-ответ с информацией о том, что компания
        была успешно скрыта.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            JsonResponse: JSON-ответ с информацией о том, что компания была успешно скрыта
        """
        view_logger = logger.bind(request=request.POST)

        data = json.load(request)
        company = data.get("company")
        try:
            await HiddenCompanies.objects.aget_or_create(
                user=request.user, name=company
            )
            view_logger.info(f"Компания {company} скрыта")
        except Exception as exc:
            view_logger.exception(exc)
        return JsonResponse({"status": f"Компания {company} скрыта"})
