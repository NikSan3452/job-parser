from logger import setup_logging

from parser.scraping.configuration import Config

setup_logging()

config = Config()


class StartScrapers:
    """Класс предназначен для запуска скраперов сайтов поиска работы."""

    @config.utils.timeit
    async def scrape_habr(self) -> None:
        """
        Асинхронный метод для скрапинга вакансий с сайта Habr.

        Returns:
            None
        """
        await config.habr_scraper.scrape()

    @config.utils.timeit
    async def scrape_geekjob(self) -> None:
        """
        Асинхронный метод для скрапинга вакансий с сайта Geekjob.

        Returns:
            None
        """
        await config.geekjob_scraper.scrape()
