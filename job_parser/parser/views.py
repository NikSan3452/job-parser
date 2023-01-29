import json
from django.http import JsonResponse
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View
from django.contrib import auth
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async

from parser import parsers
from parser.forms import SearchingForm
from parser.mixins import VacancyDataMixin
from parser.models import City, FavouriteVacancy

from profiles.models import User


class HomePageView(FormView):
    """Представление домашней страницы."""

    template_name = "parser/home.html"
    form_class = SearchingForm

    def form_valid(self, form):
        """Валидирует форму домашней страницы.

        Args:
            form: Форма.

        Returns: HTTPResponse
        """
        return super().form_valid(form)


class VacancyList(View, VacancyDataMixin):
    form_class = SearchingForm
    template_name = "parser/list.html"

    async def get_favourite_vacancy(self, request):
        """Получает список вакансий добавленных в избранное.

        Args:
            request (_type_): Запрос.

        Returns:
            _type_: Список вакансий добавленных в избранное.
        """
        try:
            user = auth.get_user(request)
            list_favourite = FavouriteVacancy.objects.filter(user=user)
            return list_favourite
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")
    
    async def get(self, request, *args, **kwargs):
        form = self.form_class()

        list_favourite = await self.get_favourite_vacancy(request)

        context = {
            "form": form,
            "object_list": VacancyDataMixin.job_list,
            "list_favourite": list_favourite,
        }

        paginator = Paginator(VacancyDataMixin.job_list, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj

        return render(request, self.template_name, context)

    async def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)

        list_favourite = await self.get_favourite_vacancy(request)

        if form.is_valid():
            city = form.cleaned_data.get("city")
            if city:
                city = city.lower()

            job = form.cleaned_data.get("job")
            if job:
                job = job.lower()

            date_from = form.cleaned_data.get("date_from")
            date_to = form.cleaned_data.get("date_to")
            title_search = form.cleaned_data.get("title_search")
            experience = int(form.cleaned_data.get("experience"))

            if (
                VacancyDataMixin.job_list is None
                or city != VacancyDataMixin.city
                or job != VacancyDataMixin.job
                or date_from != VacancyDataMixin.date_from
                or date_to != VacancyDataMixin.date_to
                or title_search != VacancyDataMixin.title_search
                or experience != VacancyDataMixin.experience
            ):
                VacancyDataMixin.job_list.clear()

                try:
                    # Получаем id города для API HeadHunter
                    if city:
                        city_from_db = await City.objects.filter(city=city).afirst()
                        city_id = city_from_db.city_id
                    else:
                        city_id = None

                    # Получаем список вакансий
                    VacancyDataMixin.job_list = await parsers.run(
                        city=city,
                        city_from_db=city_id,
                        job=job,
                        date_from=date_from,
                        date_to=date_to,
                        title_search=title_search,
                        experience=experience,
                    )
                except Exception as exc:
                    print(f"Ошибка {exc} Сервер столкнулся с непредвиденной ошибкой")

                # Присваиваем текущие значения временным переменным
                VacancyDataMixin.city = city
                VacancyDataMixin.job = job
                VacancyDataMixin.date_from = date_from
                VacancyDataMixin.date_to = date_to
                VacancyDataMixin.title_search = title_search
                VacancyDataMixin.experience = experience

            context = {
                "object_list": VacancyDataMixin.job_list,
                "city": VacancyDataMixin.city,
                "job": VacancyDataMixin.job,
                "form": form,
                "list_favourite": list_favourite,
            }

            paginator = Paginator(VacancyDataMixin.job_list, 5)
            page_number = request.POST.get("page")
            page_obj = paginator.get_page(page_number)
            context["object_list"] = page_obj

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
    vacancy_url = data.get("payload")

    if request.method == "POST":
        try:
            username = auth.get_user(request)
            FavouriteVacancy.objects.get_or_create(user=username, url=vacancy_url)
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")
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
    vacancy_url = data.get("payload")

    if request.method == "POST":
        try:
            username = auth.get_user(request)
            FavouriteVacancy.objects.filter(user=username, url=vacancy_url).delete()
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")
    return JsonResponse({"status": "Вакансия удалена из избранного"})
