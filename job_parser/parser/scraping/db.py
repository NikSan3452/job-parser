from logger import setup_logging
from loguru import logger

from parser.models import Vacancies

setup_logging()


class Database:
    """
    Класс для записи вакансий в базу данных.
    """

    async def record(self, vacancy_data: list[dict]) -> None:
        """Асинхронный метод добавления вакансий в базу данных.

        Args:
            vacancy_data (list[dict]): Данные вакансии.
        """
        try:
            await Vacancies.objects.abulk_create(
                [Vacancies(**data) for data in vacancy_data],
                ignore_conflicts=True,
            )
        except Exception as exc:
            logger.exception(exc)
