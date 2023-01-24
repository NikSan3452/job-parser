import parser.parsers as parsers
from typing import Optional
from parser.models import City


class VacancyDataMixin:
    """Класс хранит в памяти параметры поиска и информацию о найденных вакансиях"""

    city: Optional[str] = None
    job: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    title_search: bool = False
    experience: int = None

    job_list: list[dict] = []


class FormCheckMixin:
    """Класс содержит методы проверки формы по поиску вакансий"""

    async def get_request(self, request: dict) -> None:
        city_from_request = request.POST.get("city")
        if city_from_request:
            city_from_request = city_from_request.lower()

        job_from_request = request.POST.get("job")
        if job_from_request:
            job_from_request = job_from_request.lower()

        date_from = request.POST.get("date_from")
        date_to = request.POST.get("date_to")
        title_search = request.POST.get("title_search")
        experience = int(request.POST.get("experience"))

        return await self.check_form(
            city=city_from_request,
            job=job_from_request,
            date_from=date_from,
            date_to=date_to,
            title_search=title_search,
            experience=experience,
        )

    async def check_form(
        self,
        city: str,
        job: str,
        date_from: str,
        date_to: str,
        title_search: bool,
        experience: int,
    ) -> None:
        """Отвечает за проверку формы по поиску вакансий

        Args:
            city (str): Город.
            job (str): Искомая работа.
            date_from (str): Дата от.
            date_to (str): Дата до.
            title_search (bool): Checkbox, переключающий поиск по заголовкам.
        """
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

            VacancyDataMixin.city = city
            VacancyDataMixin.job = city
            VacancyDataMixin.date_from = date_from
            VacancyDataMixin.date_to = date_to
            VacancyDataMixin.title_search = title_search
            VacancyDataMixin.experience = experience
