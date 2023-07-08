import asyncio
import time

from logger import setup_logging
from loguru import logger

from parser.scraping.configuration import Config
from parser.scraping.scrapers.geekjob import GeekjobScraper
from parser.scraping.scrapers.habr import HabrScraper

setup_logging()


class StartScrapers:
    """Класс предназначен для запуска скраперов сайтов поиска работы.

    Args:
        session (aiohttp.ClientSession): Объект сессии aiohttp.
        config (Config): Объект класса Config, содержит настройки для парсера.

    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.geekjob = GeekjobScraper(self.config)
        self.habr = HabrScraper(self.config)

    async def run_scrapers(self) -> asyncio.Future[list]:
        """Запускает скраперы сайтов поиска работы.

        Создает задачи для сохранения данных с сайтов и ожидает их завершения.
        Возвращает список результатов выполнения задач.

        Returns:
            asyncio.Future[list]: Список результатов выполнения задач.

        """
        tasks: list[asyncio.Future] = []

        task1 = asyncio.create_task(self.geekjob.save())
        task2 = asyncio.create_task(self.habr.save())

        tasks.append(task1)
        tasks.append(task2)
        return await asyncio.gather(*tasks)


async def run():
    """Запускает скрапер сайтов поиска работы.

    Создает объект класса Config со всеми необходимыми параметрами,
    затем создает экземпляр класса StartParsers с переданными ему параметрами
    и вызывает его метод run_parsers.
    Выводит информацию о времени работы скрапера в лог.

    """
    config = Config()
    parser = StartScrapers(config)

    start_time = time.time()
    logger.info("Скрапер запущен")

    await parser.run_scrapers()

    logger.info("Работа скрапера завершена")
    finish_time = time.time() - start_time
    logger.debug(f"Затраченное на работу скрапера время: {round(finish_time, 2)}")


if __name__ == "__main__":
    asyncio.run(run())
