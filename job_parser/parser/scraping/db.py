from parser.scraping.scrapers.base import Scraper
from parser.scraping.fetching import Fetcher
from parser.models import Vacancies
from logger import setup_logging
from loguru import logger

setup_logging()


class Database:
    """Класс для записи полученных вакансий в базу данных
    """
    def __init__(self, scraper: Scraper, fetcher: Fetcher) -> None:
        self.scraper = scraper
        self.fetcher = fetcher
        
    async def record(self, links: list = []) -> None:
        """Сохраняет информацию о вакансиях в базе данных.

        Метод использует объект fetcher для получения ссылок на вакансии 
        и страницы вакансий. Затем он использует метод get_vacancy_details для 
        извлечения информации о вакансиях и сохраняет ее в базе данных с помощью 
        модели Vacancies.
        """
        async for page in self.fetcher.fetch_vacancy_pages(links):
            async for vacancy in self.scraper.get_vacancy_details(page):
                try:
                    await Vacancies.objects.aget_or_create(**vacancy)
                except Exception as exc:
                    logger.exception(exc)
        return None
