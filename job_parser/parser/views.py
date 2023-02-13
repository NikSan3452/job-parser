import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.contrib import auth
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required

from parser import parsers
from parser.forms import SearchingForm
from parser.mixins import VacancyHelpersMixin
from parser.models import FavouriteVacancy, VacancyBlackList


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


class VacancyListView(View, VacancyHelpersMixin):
    """Представление страницы со списком ванкасий."""

    form_class = SearchingForm
    template_name = "parser/list.html"
    job_list = []

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
        self.job_list = await self.get_data_from_cache(request)

        # Отображаем вакансии, которые в избранном
        list_favourite = await self.get_favourite_vacancy(request)

        context = {
            "form": form,
            "object_list": self.job_list,
            "list_favourite": list_favourite,
        }

        context["city"] = request_data.get("city")
        context["job"] = request_data.get("job")
        context["date_from"] = request_data.get("date_from")
        context["date_to"] = request_data.get("date_to")
        context["title_search"] = request_data.get("title_search")
        context["experience"] = request_data.get("experience")
        context["remote"] = request_data.get("remote")

        # Проверяем добавлена ли вакансия в черный список
        await self.check_vacancy_black_list(self.job_list, request)

        # Пагинация
        await self.get_pagination(request, self.job_list, context)

        return render(request, self.template_name, context)

    async def post(self, request, *args, **kwargs):
        """Отвечает за обработку POST запросов к странице со списком вакансий.

        Args:
            request: Запрос.

        Returns: HttpResponse
        """
        form = self.form_class(request.POST)

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
            ) = await self.get_form_data(form)

            # Получаем id города для API HeadHunter и Zarplata
            city_id = await self.get_city_id(city, request)

            try:
                # Получаем список вакансий
                self.job_list = await parsers.run(
                    city=city,
                    city_from_db=city_id,
                    job=job,
                    date_from=date_from,
                    date_to=date_to,
                    title_search=title_search,
                    experience=experience,
                    remote=remote,
                )
            except Exception as exc:
                print(
                    f"Ошибка в функции {self.post.__name__}: {exc} Сервер столкнулся с непредвиденной ошибкой"
                )

            # Сохраняем данные в кэше
            await self.set_data_to_cache(request, self.job_list)

            # Проверяем добавлена ли вакансия в черный список
            vacancies = await self.check_vacancy_black_list(self.job_list, request)

            context = {
                "object_list": vacancies,
                "city": city,
                "job": job,
                "date_from": date_from,
                "date_to": date_to,
                "title_search": title_search,
                "experience": experience,
                "remote": remote,
                "form": form,
            }

            # Пагинация
            await self.get_pagination(request, self.job_list, context)

        return render(request, self.template_name, context)


@login_required
def add_to_favourite_view(request):
    """Добавляет вакансию в избранное.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    data = json.load(request)
    vacancy_url = data.get("url")
    vacancy_title = data.get("title")

    if request.method == "POST":
        try:
            user = auth.get_user(request)
            FavouriteVacancy.objects.get_or_create(
                user=user, url=vacancy_url, title=vacancy_title
            )
        except Exception as exc:
            print(f"Ошибка базы данных в функции {add_to_favourite_view.__name__}: {exc}")
    return JsonResponse({"status": "Вакансия добавлена в избранное"})


@login_required
def delete_from_favourite_view(request):
    """Удаляет вакансию из избранного.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    data = json.load(request)
    vacancy_url = data.get("url")
    if request.method == "POST":
        try:
            user = auth.get_user(request)
            FavouriteVacancy.objects.filter(user=user, url=vacancy_url).delete()
        except Exception as exc:
            print(
                f"Ошибка базы данных в функции {delete_from_favourite_view.__name__}: {exc}"
            )
    return JsonResponse({"status": "Вакансия удалена из избранного"})


@login_required
def add_to_black_list_view(request):
    """Удаляет вакансию из избранного.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    data = json.load(request)
    vacancy_url = data.get("url")
    if request.method == "POST":
        try:
            user = auth.get_user(request)
            VacancyBlackList.objects.get_or_create(user=user, url=vacancy_url)
        except Exception as exc:
            print(
                f"Ошибка базы данных в функции {add_to_black_list_view.__name__}: {exc}"
            )
    return JsonResponse({"status": "Вакансия добавлена в черный список"})
