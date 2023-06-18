import asyncio
import time

import aiohttp
from loguru import logger
from logger import setup_logging

from parser.scraping.configuration import Config
from parser.scraping.scrapers.geekjob import GeekjobParser
from parser.scraping.scrapers.habr import HabrParser

setup_logging()


class StartParsers:
    """Класс предназначен для запуска скраперов сайтов поиска работы.

    Args:
        session (aiohttp.ClientSession): Объект сессии aiohttp.
        config (Config): Объект класса Config, содержит настройки для парсера.

    """
    def __init__(self, session: aiohttp.ClientSession, config: Config) -> None:
        self.session = session
        self.config = config

        self.geekjob_parser = GeekjobParser(config, session)
        self.habr_parser = HabrParser(config, session)

    async def run_parsers(self) -> asyncio.Future[list]:
        """Запускает скраперы сайтов поиска работы.

        Создает задачи для сохранения данных с сайтов geekjob.ru и career.habr.com и 
        ожидает их завершения. Возвращает список результатов выполнения задач.

        Returns:
            asyncio.Future[list]: Список результатов выполнения задач.

        """
        tasks: list[asyncio.Future] = []

        task1 = asyncio.create_task(self.geekjob_parser.save_data())
        task2 = asyncio.create_task(self.habr_parser.save_data())
        tasks.append(task1)
        tasks.append(task2)
        return await asyncio.gather(*tasks)


async def run():
    """Запускает скрапер сайтов поиска работы.

    Создает объект сессии aiohttp и объект класса Config. Затем создает объект класса 
    StartParsers и вызывает его метод run_parsers. 
    Выводит информацию о времени работы скрапера в лог.

    """
    async with aiohttp.ClientSession() as session:
        config = Config()
        parser = StartParsers(session, config)

        start_time = time.time()
        logger.info("Скрапер запущен")

        await parser.run_parsers()

        logger.info("Работа скрапера завершена")
        finish_time = time.time() - start_time
        logger.debug(f"Затраченное на работу скрапера время: {round(finish_time, 2)}")


if __name__ == "__main__":
    asyncio.run(run())
