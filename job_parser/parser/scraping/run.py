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

    async def save_geekjob_data(self) -> int:
        """Сохраняет данные с сайта Geekjob в базе."""
        geekjob_fetcher = Fetcher(
            config.GEEKJOB_URL, self.session, config.GEEKJOB_PAGES_COUNT
        )
        geekjob_links = await geekjob_fetcher.fetch_vacancy_links("Geekjob")
        geekjob_parser = GeekjobParser(geekjob_fetcher)
        vacancy_counter = 0

        async for page in geekjob_fetcher.fetch_vacancy_pages(geekjob_links):
            async for vacancy in geekjob_parser.get_vacancy_details(page):
                try:
                    await VacancyScraper.objects.aget_or_create(**vacancy)
                    logger.debug("Вакансия успешно записана в базу")
                except (Error, IntegrityError, DatabaseError, ProgrammingError) as exc:
                    logger.exception(exc)
                vacancy_counter += 1
        return vacancy_counter

    async def save_habr_data(self) -> int:
        """Сохраняет данные с сайта Habr career в базе."""
        habr_fetcher = Fetcher(config.HABR_URL, self.session, config.HABR_PAGES_COUNT)
        habr_links = await habr_fetcher.fetch_vacancy_links("Habr")
        habr_parser = HabrParser(habr_fetcher)
        vacancy_counter = 0

        async for page in habr_fetcher.fetch_vacancy_pages(habr_links):
            async for vacancy in habr_parser.get_vacancy_details(page):
                try:
                    await VacancyScraper.objects.aget_or_create(**vacancy)
                    logger.debug("Вакансия успешно записана в базу")
                except (Error, IntegrityError, DatabaseError, ProgrammingError) as exc:
                    logger.exception(exc)
                vacancy_counter += 1
        return vacancy_counter

    async def run_parsers(self) -> asyncio.Future[list]:
        """Запускает асинхронные задачи парсеров."""
        tasks: list[asyncio.Future] = []
        task1 = asyncio.create_task(self.save_geekjob_data())
        task2 = asyncio.create_task(self.save_habr_data())
        tasks.append(task1)
        tasks.append(task2)
        logger.debug(
            f"Количество вакансий записанных в базу: {await task1 + await task2}"
        )
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
