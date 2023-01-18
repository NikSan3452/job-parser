from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View
from parser.models import City

from parser.forms import SearchingForm
from parser.mixins import VacancyDataMixin, FormCheckMixin
import parsers


class HomePageView(View, VacancyDataMixin, FormCheckMixin):
    async def get(self, request, *args, **kwargs):
        form = SearchingForm()

        context = {
            "form": form,
        }

        return render(
            request=request,
            template_name="parser/home.html",
            context=context,
        )

    async def post(self, request, *args, **kwargs):
        form = SearchingForm(request.POST)

        city_from_request = request.POST.get("city")
        if city_from_request:
            city_from_request = city_from_request.lower()

        job_from_request = request.POST.get("job")
        if job_from_request:
            job_from_request = job_from_request.lower()

        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        title_search = request.POST.get("title_search")

        await self.check_form(
            city=city_from_request,
            job=job_from_request,
            date_from=date_from,
            date_to=date_to,
            title_search=title_search,
        )

        context = {
            "form": form,
        }

        return render(
            request=request,
            template_name="parser/home.html",
            context=context,
        )


class VacancyList(View, VacancyDataMixin, FormCheckMixin):
    async def get(self, request, *args, **kwargs):
        form = SearchingForm()

        context = {
            "object_list": VacancyDataMixin.job_list,
            "form": form,
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

    async def post(self, request, *args, **kwargs):
        form = SearchingForm(request.POST)

        city_from_request = request.POST.get("city")
        if city_from_request:
            city_from_request = city_from_request.lower()

        job_from_request = request.POST.get("job")
        if job_from_request:
            job_from_request = job_from_request.lower()

        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        title_search = request.POST.get("title_search")

        await self.check_form(
            city=city_from_request,
            job=job_from_request,
            date_from=date_from,
            date_to=date_to,
            title_search=title_search,
        )

        context = {
            "object_list": VacancyDataMixin.job_list,
            "city": VacancyDataMixin.city,
            "job": VacancyDataMixin.job,
            "form": form,
        }

        paginator = Paginator(VacancyDataMixin.job_list, 5)
        page_number = request.POST.get("page")
        page_obj = paginator.get_page(page_number)
        context["object_list"] = page_obj

        return render(
            request=request,
            template_name="parser/list.html",
            context=context,
        )
