from typing import Any, Dict
from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View
from django.http import HttpResponse

from parser.parsers import HeadHunterParser
from parser.forms import SearchingForm
from parser.models import City
from parser.mixins import VacancyDataMixin


def homepage(request):
    form = SearchingForm()
    return render(
        request=request,
        template_name="parser/home.html",
        context={"form": form},
    )


# RESULT = None
# CITY_FROM_REQUEST = None
# JOB_FROM_REQUEST = None


# def list_view(request):
#     global CITY_FROM_REQUEST
#     global JOB_FROM_REQUEST

#     city_from_request = request.GET.get("city")
#     if city_from_request:
#         city_from_request = city_from_request.lower()

#     job_from_request = request.GET.get("job")
#     if job_from_request:
#         job_from_request = job_from_request.lower()

#     form = SearchingForm()
#     city_from_db = City.objects.filter(city=city_from_request).first()
#     hh = HeadHunterParser(job=job_from_request, area=city_from_db.hh_id)
#     global RESULT
#     if (
#         RESULT is None
#         or city_from_request != CITY_FROM_REQUEST
#         or job_from_request != JOB_FROM_REQUEST
#     ):
#         RESULT = hh.read_jobs()[0]["items"]
#         if CITY_FROM_REQUEST is None:
#             CITY_FROM_REQUEST = city_from_request
#         if JOB_FROM_REQUEST is None:
#             JOB_FROM_REQUEST = job_from_request

#     context = {
#         "object_list": RESULT,
#         "city": CITY_FROM_REQUEST,
#         "job": JOB_FROM_REQUEST,
#         "form": form,
#     }
#     paginator = Paginator(RESULT, 5)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)
#     context["object_list"] = page_obj
#     return render(request=request, template_name="parser/list.html", context=context)


class VacancyList(View, VacancyDataMixin):
    form = SearchingForm()

    def get(self, request, *args, **kwargs):
        city_from_request = request.GET.get("city")
        if city_from_request:
            city_from_request = city_from_request.lower()

        job_from_request = request.GET.get("job")
        if job_from_request:
            job_from_request = job_from_request.lower()

        # Проверяем город на наличием в БД и получем его id
        city_from_db = City.objects.filter(city=city_from_request).first()
        if city_from_db is None:
            return HttpResponse('Такого горад нет в базе данных')
        # Находим вакансии по паре город-специальность
        hh = HeadHunterParser(job=job_from_request, area=city_from_db.hh_id)

        if (  # Если список вакансий пуст
            VacancyDataMixin.job_list is None
            # или город из формы не равен городу из предыдущего запроса
            or city_from_request != VacancyDataMixin.city
            # или вакансия из формы не равна вакансии из предыдущего запроса
            or job_from_request != VacancyDataMixin.job
        ):  # Получаем список вакансий
            VacancyDataMixin.job_list = hh.read_jobs()[0]["items"]
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
