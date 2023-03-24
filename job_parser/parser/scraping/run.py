import asyncio
import time

import aiohttp
from django.db import DatabaseError, Error, IntegrityError, ProgrammingError
from logger import logger, setup_logging
from parser.models import VacancyScraper
from parser.scraping.configuration import Config
from parser.scraping.fetching import Fetcher
from parser.scraping.parsers.geekjob import GeekjobParser
from parser.scraping.parsers.habr import HabrParser

setup_logging()


config = Config()


class StartParsers:
    """Запуск парсеров"""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def initial_params(self) -> None:
        """Инициализирует параметры парсера."""
        self.geekjob_fetcher = Fetcher(
            config.GEEKJOB_URL, self.session, config.GEEKJOB_PAGES_COUNT
        )
        self.habr_fetcher = Fetcher(
            config.HABR_URL, self.session, config.HABR_PAGES_COUNT
        )

        self.geekjob_parser = GeekjobParser(self.geekjob_fetcher)
        self.habr_parser = HabrParser(self.habr_fetcher)

        self.geekjob_links = await self.geekjob_fetcher.fetch_vacancy_links("Geekjob")
        self.habr_links = await self.habr_fetcher.fetch_vacancy_links("Habr")

    async def save_data(
        self, links: list[str], fetcher: Fetcher, parser: GeekjobParser | HabrParser
    ) -> int:
        """Сохраняет данные в БД.

        Args:
            links (list[str]): Список ссылок на страницы с вакансиями.
            fetcher (Fetcher): Экземпляр класса Fetcher.
            parser (GeekjobParser | HabrParser): Экземпляр класса парсера.

        Returns:
            int: Количество объектов записанных в БД.
        """
        vacancy_counter = 0
        async for page in fetcher.fetch_vacancy_pages(links):
            async for vacancy in parser.get_vacancy_details(page):
                try:
                    await VacancyScraper.objects.aget_or_create(**vacancy)
                except (Error, IntegrityError, DatabaseError, ProgrammingError) as exc:
                    logger.exception(exc)
                vacancy_counter += 1
        return vacancy_counter

    async def run_parsers(self) -> asyncio.Future[list]:
        """Запускает асинхронные задачи парсеров."""
        tasks: list[asyncio.Future] = []
        await self.initial_params()
        task1 = asyncio.create_task(
            self.save_data(
                self.geekjob_links, self.geekjob_fetcher, self.geekjob_parser
            )
        )
        task2 = asyncio.create_task(
            self.save_data(self.habr_links, self.habr_fetcher, self.habr_parser)
        )
        tasks.append(task1)
        tasks.append(task2)
        logger.debug(f"Вакансий записано в базу: {await task1 + await task2}")
        return await asyncio.gather(*tasks)


async def run():
    """Запуск скрипта"""
    async with aiohttp.ClientSession() as session:
        parser = StartParsers(session)

        start_time = time.time()
        logger.info("Парсер запущен")

        await parser.run_parsers()

        logger.info("Работа парсера завершена")
        finish_time = time.time() - start_time
        logger.debug(f"Затраченное на работу скрипта время: {round(finish_time, 2)}")


if __name__ == "__main__":
    asyncio.run(run())
