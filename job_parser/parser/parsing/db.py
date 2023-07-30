from loguru import logger
from parser.parsing.parsers.base import Vacancy

from parser.models import Vacancies


class Database:
    """
    Класс для записи вакансий в базу данных.
    """

    async def record(self, vacancy_data: list[Vacancy]) -> None:
        """Асинхронный метод добавления вакансий в базу данных.

        Args:
            vacancy_data (list[Vacancy]): Данные вакансии.
        """
        try:
            await Vacancies.objects.abulk_create(
                [Vacancies(**data.__dict__) for data in vacancy_data],
                ignore_conflicts=True,
            )
        except Exception as exc:
            logger.exception(exc)
