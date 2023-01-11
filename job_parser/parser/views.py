from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponse

from parser.parsers import HeadHunterParser
from parser.forms import SearchingForm
from parser.models import City
from parser.mixins import VacancyDataMixin


class HomePageView(TemplateView):
    template_name = "parser/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SearchingForm
        return context


class VacancyList(View, VacancyDataMixin):
    form = SearchingForm()

    async def get(self, request, *args, **kwargs):
        city_from_request = request.GET.get("city")
        if city_from_request:
            city_from_request = city_from_request.lower()

        job_from_request = request.GET.get("job")
        if job_from_request:
            job_from_request = job_from_request.lower()

        # Проверяем город на наличием в БД и получем его id
        city_from_db = await City.objects.filter(city=city_from_request).afirst()
        if city_from_db is None:
            return HttpResponse("Такого города нет в базе данных")
        # Находим вакансии по паре город-специальность
        hh = HeadHunterParser(job=job_from_request, area=city_from_db.hh_id)

        if (  # Если список вакансий пуст
            VacancyDataMixin.job_list is None
            # или город из формы не равен городу из предыдущего запроса
            or city_from_request != VacancyDataMixin.city
            # или вакансия из формы не равна вакансии из предыдущего запроса
            or job_from_request != VacancyDataMixin.job
        ):  # Получаем список вакансий
            VacancyDataMixin.job_list = (await hh.read_jobs())[0]["items"]
            # Присваиваем временным переменным значения текущего города и вакансии
            VacancyDataMixin.city = city_from_request
            VacancyDataMixin.job = job_from_request

        context = {
            "object_list": VacancyDataMixin.job_list,
            "city": VacancyDataMixin.city,
            "job": VacancyDataMixin.job,
            "form": self.form,
        }

        paginator = Paginator(VacancyDataMixin.job_list, 5)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj

        return render(
            request=request,
            template_name="parser/list.html",
            context=context,
        )
