from typing import TYPE_CHECKING

from logger import setup_logging

if TYPE_CHECKING:
    from ..config import ParserConfig

from .base import Vacancy
from .headhunter import Headhunter

# Логирование
setup_logging()


class Zarplata(Headhunter):
    """Класс для парсинга вакансий с сайта Zarplata.

    Наследуется от класса Headhunter.
    Класс Zarplata предназначен для парсинга вакансий с сайта Zarplata.
    Он содержит метод parsing_vacancy_zarplata для выполнения парсинга вакансий с
    этого сайта.
    Остальные методы наследуются от родительского класса Headhunter.
    """

    def __init__(self, config: "ParserConfig") -> None:
        super().__init__(config, "zp")

    async def parse(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с сайта Zarplata.

        Метод вызывает метод parse родительского класса Parser
        с параметрами запроса.

        Returns: None.
        """
        return await super().parse()
