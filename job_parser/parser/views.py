import json
from parser.api import main
from parser.api.utils import Utils
from parser.forms import SearchingForm
from parser.mixins import (
    AsyncLoginRequiredMixin,
    RedisCacheMixin,
    VacancyHelpersMixin,
    VacancyScraperMixin,
)
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList

from django.db import DatabaseError, IntegrityError
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
    """
    Класс представления для отображения списка вакансий.

    Этот класс наследуется от классов `View`, `RedisCacheMixin`, `VacancyHelpersMixin`
    и `VacancyScraperMixin`.
    Он использует форму `SearchingForm` и шаблон "parser/list.html" для отображения
    списка вакансий.
    Список вакансий получается из API и сохраняется в атрибуте `job_list_from_api`.

    Attributes:
        form_class (Form): Форма для поиска вакансий.
        template_name (str): Имя шаблона для отображения списка вакансий.
        job_list_from_api (list[dict]): Список вакансий из API.
    """

    form_class: SearchingForm = SearchingForm
    template_name: str = "parser/list.html"
    job_list_from_api: list[dict] = []

    @logger.catch(level="CRITICAL", message="Ошибка в методе <VacancyListView.get()>")
    async def get(self, request: HttpRequest) -> TemplateResponse:
        """
        Метод обработки GET-запроса для отображения списка вакансий.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода проверяются данные запроса с помощью метода `check_request_data`.
        Затем создается форма с начальными данными из запроса, а также ключ кэша
        с помощью метода `create_cache_key`.
        Далее получается список вакансий из кэша с помощью метода `get_data_from_cache`.
        Если пользователь аутентифицирован, то список вакансий фильтруется с помощью
        методов `check_company_in_hidden_list` и `check_vacancy_in_black_list`.
        Также получается список избранных вакансий с помощью метода `get_favourite_vacancy`.
        Список вакансий сортируется по дате с помощью функции `sort_by_date`
        из модуля `utils`.
        В контекст добавляются данные формы, отфильтрованный список вакансий
        и список избранных вакансий.
        Также добавляются данные из запроса и выполняется пагинация с помощью
        метода `get_pagination`.
        В конце метода возвращается ответ с использованием шаблона.

        Args:
            request (HttpRequest): Объект запроса

        Returns:
            TemplateResponse: Ответ с использованием шаблона
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
            **request_data,
        }

        # Пагинация
        await self.get_pagination(request, sorted_job_list, context)

        return TemplateResponse(request, self.template_name, context)

    async def post(self, request: HttpRequest) -> TemplateResponse:
        """
        Метод обработки POST-запроса для отображения списка вакансий.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается форма `form` с данными из запроса и проверяется
        ее валидность.
        Если форма валидна, то из нее извлекаются данные с помощью метода `get_form_data`
        и сохраняются в переменной `params`.
        Затем из переменной `params` извлекается город и выполняется поиск
        его идентификатора с помощью метода `get_city_id`.
        Полученный идентификатор города добавляется в переменную `params`.
        Далее создается пустой список `job_list_from_scraper` для хранения
        вакансий из скрапера.
        В блоке try выполняется поиск вакансий с помощью скрапера или API в зависимости
        от выбранной площадки.
        Если выбраны площадки из скрапера, то список вакансий из API очищается
        и выполняется поиск вакансий с помощью скрапера.
        Иначе список вакансий из API очищается и заполняется данными из API,
        а затем выполняется поиск вакансий с помощью скрапера.
        В случае возникновения исключения оно записывается в лог.

        После выполнения поиска списки вакансий из API и скрапера объединяются
        с помощью метода `add_vacancy_to_job_list_from_api` и сохраняются
        в переменной `shared_job_list`.
        Если пользователь аутентифицирован, то список вакансий фильтруется с помощью
        методов `check_company_in_hidden_list` и `check_vacancy_in_black_list`.
        Также получается список избранных вакансий с помощью метода
        `get_favourite_vacancy` и сохраняется в переменной `list_favourite`.
        Отфильтрованный список вакансий сортируется по дате с помощью функции
        `sort_by_date` из модуля `utils`.
        Затем создается ключ кэша с помощью метода `create_cache_key` и отфильтрованный
        список вакансий сохраняется в кэше с помощью метода `set_data_to_cache`.
        В контекст добавляются данные формы, отфильтрованный список вакансий
        и список избранных вакансий.
        Также выполняется пагинация с помощью метода `get_pagination`.
        В конце метода возвращается ответ с использованием шаблона.

        Args:
            request (HttpRequest): Объект запроса
            *args: Позиционные аргументы
            **kwargs: Именованные аргументы

        Returns:
            TemplateResponse: Ответ с использованием шаблона
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
            "form": form,
            "object_list": sorted_shared_job_list,
            "list_favourite": list_favourite,
            **params,
        }

        # Пагинация
        await self.get_pagination(request, sorted_shared_job_list, context)

        return TemplateResponse(request, self.template_name, context)


class AddVacancyToFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в избранное.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в избранное.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса  десериализуются в блоке try/except и случае успеха
        загружаются в переменную `data`, из которой извлекается URL
        и название вакансии. В противном случае будет вызвано исключение JSONDecodeError
        с последующей отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL и название вакансии вакансии отсутствуют будет возвращен
        соответствующий JsonResponse со статусом 400.
        Затем метод пытается создать или получить объект `FavouriteVacancy`
        с указанными данными пользователя, URL и названием вакансии.
        Если все прошло успешно, в лог записывается информация об успешном добавлении
        вакансии в избранное.
        В случае возникновения исключения IntegrityError или DatabaseError они записываются
        в лог и будет возвращен соответствующий JsonResponse со статусом 400 или 500.
        В конце метода возвращается JSON-ответ с информацией об успешном добавлении
        вакансии в избранное.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешном добавлении вакансии в избранное.
        """
        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        vacancy_url = data.get("url")
        vacancy_title = data.get("title")
        if not vacancy_url or not vacancy_title:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            await FavouriteVacancy.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            view_logger.info(f"Вакансия {vacancy_title} добавлена в избранное")
        except IntegrityError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Такая вакансия уже есть в избранном"}, status=400
            )
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Произошла ошибка базы данных"},
                status=500,
            )

        return JsonResponse(
            {"status": f"Вакансия {vacancy_title} добавлена в избранное"}
        )


class DeleteVacancyFromFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из списка избранных.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на удаление вакансии из избранного.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается получить объект `FavouriteVacancy` с указанными данными
        пользователя и URL вакансии. Если объект существует, он удаляется, и в лог
        записывается информация об успешном удалении вакансии из избранного.
        В случае возникновения исключения DatabaseError оно записывается в лог и
        будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешном удалении
        вакансии из избранного.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном удалении
            вакансии из избранного.
        """
        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        vacancy_url = data.get("url")
        if not vacancy_url:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            obj = await FavouriteVacancy.objects.filter(
                user=request.user, url=vacancy_url
            ).afirst()
            if not obj:
                return JsonResponse(
                    {"Ошибка": f"Вакансия {vacancy_url} не найдена"}, status=404
                )
            else:
                obj.delete()
                view_logger.info(f"Вакансия {vacancy_url} удалена из избранного")
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)
        return JsonResponse({"status": f"Вакансия {vacancy_url} удалена из избранного"})


class AddVacancyToBlackListView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в черный список.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в черный список.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается создать или получить объект `VacancyBlackList`
        с указанными данными пользователя, URL и названием вакансии.
        Если все прошло успешно, в лог записывается информация об успешном добавлении
        вакансии в черный список. Также удаляется объект `FavouriteVacancy`, если он
        существует.
        В случае возникновения исключения DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешном добавлении
        вакансии в черный список.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном добавлении
            вакансии в черный список.
        """

        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        vacancy_url = data.get("url")
        vacancy_title = data.get("title")
        if not vacancy_url or not vacancy_title:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            await VacancyBlackList.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            await FavouriteVacancy.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} добавлена в черный список")
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse(
            {"status": f"Вакансия {vacancy_url} добавлена в черный список"}
        )


class HideCompanyView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для сокрытия вакансий выбранных компаний.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на скрытие компании.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается создать или получить объект `HiddenCompanies`
        с указанными данными пользователя и названием компании.
        Если все прошло успешно, в лог записывается информация о том,
        что компания была скрыта.
        В случае возникновения исключения DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что компания была скрыта.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была скрыта.
        """
        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        company = data.get("company")
        if not company:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            await HiddenCompanies.objects.aget_or_create(
                user=request.user, name=company
            )
            view_logger.info(f"Компания {company} скрыта")
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": f"Компания {company} скрыта"})


class DeleteFromBlacklistView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из черного списка.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление вакансии из черного списка.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается удалить объект `VacancyBlackList`
        с указанными данными пользователя и URL вакансии.
        Если все прошло успешно, в лог записывается информация о том,
        что вакансия была удалена из черного списка.
        В случае возникновения исключений DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что вакансия была удалена из черного списка.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что вакансия была удалена из черного списка.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            data = json.load(request)
            vacancy_url = data.get("url")
            if not vacancy_url:
                return JsonResponse(
                    {"Ошибка": "Отсутствует обязательное поле 'url'"}, status=400
                )

            await VacancyBlackList.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} удалена из черного списка")
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse(
            {"status": f"Вакансия {vacancy_url} удалена из черного списка"}
        )


class DeleteFromHiddenCompaniesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления компании из списка скрытых.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление компании из списка скрытых.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается удалить объект `HiddenCompanies`
        с указанными данными пользователя и названием компании.
        Если все прошло успешно, в лог записывается информация о том,
        что компания была удалена из списка скрытых.
        В случае возникновения исключений DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что компания была удалена из списка скрытых.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была удалена из списка скрытых.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            data = json.load(request)
            company = data.get("name")
            if not company:
                return JsonResponse(
                    {"Ошибка": "Отсутствует обязательное поле 'name'"}, status=400
                )

            await HiddenCompanies.objects.filter(
                user=request.user, name=company
            ).adelete()
            view_logger.info(f"Компания {company} удалена из списка скрытых")
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": f"Компания {company} удалена из списка скрытых"})
