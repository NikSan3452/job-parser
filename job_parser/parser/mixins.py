import parsers
from typing import Optional
from parser.models import City


class VacancyDataMixin:
    """Класс хранит в памяти параметры поиска и информацию о найденных вакансиях"""

    city: Optional[str] = None
    job: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    title_search: bool = False

    job_list: list[dict] = []


class FormCheckMixin:
    """Класс содержит методы проверки формы по поиску вакансий"""

    async def check_form(
        self, city: str, job: str, date_from: str, date_to: str, title_search: bool
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
        ):
            VacancyDataMixin.job_list.clear()

            try:
                # Получаем id города для API HeadHunter
                city_from_db = await City.objects.filter(city=city).afirst()

                # Получаем список вакансий
                VacancyDataMixin.job_list = await parsers.run(
                    city=city,
                    city_from_db=city_from_db.hh_id,
                    job=job,
                    date_from=date_from,
                    date_to=date_to,
                    title_search=title_search,
                )
            except Exception as exc:
                print(f"Ошибка {exc} Сервер столкнулся с непредвиденной ошибкой")

            VacancyDataMixin.city = city
            VacancyDataMixin.job = city
            VacancyDataMixin.date_from = date_from
            VacancyDataMixin.date_to = date_to
            VacancyDataMixin.title_search = title_search
