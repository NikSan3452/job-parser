import asyncio
import time
from parser.parsing.config import ParserConfig
from parser.parsing.parsers import Headhunter, SuperJob, Trudvsem, Zarplata
from typing import Any

from logger import logger, setup_logging

# Логирование
setup_logging()

config = ParserConfig()

class JobParser:
    """
    Класс для парсинга вакансий.

    Класс содержит методы для парсинга вакансий с различных сайтов. При инициализации 
    объекта класса создаются объекты классов `Headhunter`, `SuperJob`, `Zarplata` 
    и `Trudvsem`, которые используются для парсинга вакансий с соответствующих сайтов.

    Attributes:
        hh (Headhunter): Объект класса `Headhunter` для парсинга вакансий с сайта 
        HeadHunter.
        sj (SuperJob): Объект класса `SuperJob` для парсинга вакансий с сайта SuperJob.
        zp (Zarplata): Объект класса `Zarplata` для парсинга вакансий с сайта Zarplata.
        tv (Trudvsem): Объект класса `Trudvsem` для парсинга вакансий с сайта Trudvsem.
    """

    def __init__(self) -> None:
        self.hh = Headhunter(config)
        self.sj = SuperJob(config)
        self.zp = Zarplata(config)
        self.tv = Trudvsem(config)

    async def parse_vacancies(self) -> None:
        """
        Асинхронный метод для парсинга вакансий.

        Метод запускает параллельно 4 задачи для парсинга вакансий с сайтов 
        HeadHunter, SuperJob, Zarplata и Trudvsem.

        Returns:
            None
        """
        task1 = asyncio.create_task(self.hh.parsing_vacancy_headhunter())
        task2 = asyncio.create_task(self.zp.parsing_vacancy_zarplata())
        task3 = asyncio.create_task(self.sj.parsing_vacancy_superjob())
        task4 = asyncio.create_task(self.tv.parsing_vacancy_trudvsem())

        await asyncio.gather(
            task1,
            task2,
            task3,
            task4,
        )

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
    parser = JobParser()
    
    await parser.parse_vacancies()

    end = time.time() - start
    logger.debug(f"Затраченное на работу парсера время: {round(end, 2)}")
