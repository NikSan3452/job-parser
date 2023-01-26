from django.shortcuts import render
from django.core.paginator import Paginator
from django.views import View

from parser.forms import SearchingForm
from parser.mixins import VacancyDataMixin, FormCheckMixin
from django.views.generic.edit import FormView


class HomePageView(FormView):
    template_name = "parser/home.html"
    form_class = SearchingForm

    def form_valid(self, form):
        return super().form_valid(form)


class VacancyList(View, VacancyDataMixin, FormCheckMixin):
    async def get(self, request, *args, **kwargs):
        form = SearchingForm()

        context = {
            "object_list": VacancyDataMixin.job_list,
            "form": form,
        }

        return render(
            request=request,
            template_name="parser/list.html",
            context=context,
        )

    async def post(self, request, *args, **kwargs):
        form = SearchingForm(request.POST)

        await self.get_request(request=request)

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
