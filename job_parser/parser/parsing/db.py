
from loguru import logger
from parser.models import Vacancies


class Database:
    """
    Класс для записи вакансий в базу данных.
    """
    async def add_vacancy_to_database(self, vacancy_data: Vacancies) -> None:
        """Асинхронный метод добавления вакансий в базу данных.

        Args:
            vacancy_data (Vacancy): Данные вакансии.
        """
        try:
            await Vacancies.objects.aget_or_create(**vacancy_data.__dict__)
        except Exception as exc:
            logger.exception(exc)