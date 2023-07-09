import asyncio
import time

from logger import setup_logging
from loguru import logger

from parser.scraping.configuration import Config

setup_logging()


class StartScrapers:
    """Класс предназначен для запуска скраперов сайтов поиска работы.

    Args:
        config (Config): Объект класса Config, содержит настройки для парсера.

    """

    def __init__(self, config: Config) -> None:
        self.config = config

    async def start(self) -> list:
        """Запускает скраперы сайтов поиска работы.

        Создает задачи для сохранения данных с сайтов и ожидает их завершения.
        Возвращает список результатов выполнения задач.

        Returns:
            list: Список результатов выполнения задач.

        """
        tasks = [
            asyncio.create_task(scraper.save()) for scraper in self.config.scrapers
        ]
        return await asyncio.gather(*tasks)


async def main():
    """Запускает скрапер сайтов поиска работы.

    Создает объект класса Config со всеми необходимыми параметрами,
    затем создает экземпляр класса StartParsers с переданными ему параметрами
    и вызывает его метод run_parsers.
    Выводит информацию о времени работы скрапера в лог.

    """
    config = Config()
    scrapers = StartScrapers(config)

    start_time = time.time()
    logger.info("Скрапер запущен")

    await scrapers.start()

    logger.info("Работа скрапера завершена")
    finish_time = time.time() - start_time
    logger.debug(f"Затраченное на работу скрапера время: {round(finish_time, 2)}")


if __name__ == "__main__":
    asyncio.run(main())
