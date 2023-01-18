import parsers
from parser.models import City


class VacancyDataMixin:
    city = None
    job = None
    date_from = None
    date_to = None
    order_by = None
    title_search = False

    job_list = []


class FormCheckMixin:
    async def check_form(
        self, city: str, job: str, date_from: str, date_to: str, title_search: bool
    ) -> None:
        if (
            VacancyDataMixin.job_list is None
            or city != VacancyDataMixin.city
            or job != VacancyDataMixin.job
            or date_from != VacancyDataMixin.date_from
            or date_to != VacancyDataMixin.date_to
            or title_search != VacancyDataMixin.title_search
        ):  # Получаем список вакансий
            VacancyDataMixin.job_list.clear()
            city_from_db = await City.objects.filter(city=city).afirst()
            VacancyDataMixin.job_list = await parsers.run(
                city=city,
                city_from_db=city_from_db.hh_id,
                job=job,
                date_from=date_from,
                date_to=date_to,
                title_search=title_search,
            )

            VacancyDataMixin.city = city
            VacancyDataMixin.job = city
            VacancyDataMixin.date_from = date_from
            VacancyDataMixin.date_to = date_to
            VacancyDataMixin.title_search = title_search
