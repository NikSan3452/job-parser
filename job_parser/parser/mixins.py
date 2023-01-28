class VacancyDataMixin:
    """Класс хранит в памяти параметры поиска и информацию о найденных вакансиях"""

    city: str = None
    job: str = None
    date_from: str = None
    date_to: str = None
    title_search: bool = False
    experience: int = None

    job_list: list[dict] = []
