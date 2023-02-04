from django.contrib import auth
from parser.models import FavouriteVacancy, VacancyBlackList


class VacancyDataMixin:
    """Класс хранит в памяти параметры поиска и информацию о найденных вакансиях"""

    city: str = None
    job: str = None
    date_from: str = None
    date_to: str = None
    title_search: bool = False
    experience: int = None

    job_list: list[dict] = []


class VacancyHelpersMixin:
    """Класс предоставляет вспомогательные методы"""

    async def check_vacancy_black_list(
        self, vacancies: list[dict], request: dict
    ) -> list[dict]:
        """Проверяет добавлена ли вакансия в черный список
        и есла да, то удаляет ее из выдачи и избранного.

        Args:
            vacancies (list[dict]): Список вакансий из API.
            request (dict): Запрос.

        Returns:
            list[dict]: Список вакансий без добавленных в черный список.
        """
        try:
            user = auth.get_user(request)

            for vacancy in vacancies.copy():
                async for job in VacancyBlackList.objects.all():
                    if vacancy["url"] == job.url:
                        try:
                            FavouriteVacancy.objects.filter(
                                user=user, url=vacancy["url"]
                            ).delete()
                        except:
                            pass
                        vacancies.remove(vacancy)
            return vacancies
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")

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
