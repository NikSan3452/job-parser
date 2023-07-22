import asyncio
import time
from parser.parsing.config import ParserConfig
from typing import Any

from logger import logger, setup_logging

# Логирование
setup_logging()


class JobParser:
    """
    Класс для парсинга вакансий.

    Класс содержит методы для парсинга вакансий с различных сайтов. При инициализации
    объекта класса создаются объекты классов `Headhunter`, `SuperJob`, `Zarplata`
    и `Trudvsem`, которые используются для парсинга вакансий с соответствующих сайтов.

    Attributes:
        (Headhunter): Объект класса `Headhunter` для парсинга вакансий с сайта
        HeadHunter.
        (SuperJob): Объект класса `SuperJob` для парсинга вакансий с сайта SuperJob.
        (Zarplata): Объект класса `Zarplata` для парсинга вакансий с сайта Zarplata.
        (Trudvsem): Объект класса `Trudvsem` для парсинга вакансий с сайта Trudvsem.
    """

    def __init__(self, config: ParserConfig) -> None:
        self.config = config

    async def parse_vacancies(self) -> None:
        """
        Асинхронный метод для парсинга вакансий.

        Метод запускает задачи для парсинга вакансий с сайтов поиску работы.

        Returns:
            None
        """
        tasks = [asyncio.create_task(parser.parse()) for parser in self.config.parsers]
        await asyncio.gather(*tasks)


async def start() -> Any:
    """
    Асинхронная функция для запуска парсинга вакансий.

    Функция создает объект класса `JobParser`, затем вызывает его метод
    `parse_vacancies` для парсинга. В конце работы функции выводится сообщение с
    информацией о времени, затраченном на работу парсера.

    Returns:
        Any
    """
    start = time.time()

    config = ParserConfig()
    parser = JobParser(config)

    await parser.parse_vacancies()

    end = time.time() - start
    logger.debug(f"Затраченное на работу парсера время: {round(end, 2)}")
