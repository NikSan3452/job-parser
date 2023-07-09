from logger import setup_logging

from ..config import ParserConfig
from ...utils import Utils
from .headhunter import Headhunter
from .base import Vacancy

# Логирование
setup_logging()

utils = Utils()


class Zarplata(Headhunter):
    """Класс для парсинга вакансий с сайта Zarplata.

    Наследуется от класса Headhunter.
    Класс Zarplata предназначен для парсинга вакансий с сайта Zarplata.
    Он содержит метод parsing_vacancy_zarplata для выполнения парсинга вакансий с
    этого сайта.
    Остальные методы наследуются от родительского класса Headhunter.
    """

    def __init__(self, config: ParserConfig) -> None:
        super().__init__(config, "zp")

    async def parse(self) -> Vacancy | None:
        """
        Асинхронный метод для парсинга вакансий с сайта Zarplata.

        Метод вызывает метод vacancy_parsing родительского класса Parser
        с параметрами запроса.

        Returns:
            dict: Словарь с результатом выполнения метода.
        """
        return await super().vacancy_parsing()
