import os
from dataclasses import dataclass, field

from fake_useragent import UserAgent
from parser.scraping.scrapers.geekjob import GeekjobScraper
from parser.scraping.scrapers.habr import HabrScraper

from parser.scraping.fetching import Fetcher
from parser.utils import Utils


@dataclass
class Config:
    """Класс описывает конфигурацию парсеров."""

    # GEEKJOB
    geekjob_domain: str = "https://geekjob.ru"
    geekjob_uri: str = "vacancies"
    geekjob_url: str = f"{geekjob_domain}/{geekjob_uri}/"
    geekjob_job_board: str = "Geekjob"
    geekjob_pages_count: int = int(os.getenv("GEEKJOB_PAGES_COUNT", 5))

    # HABR
    habr_domain: str = "https://career.habr.com"
    habr_uri: str = "vacancies?sort=date&type=all&page="
    habr_url: str = f"{habr_domain}/{habr_uri}"
    habr_job_board: str = "Habr"
    habr_pages_count: int = int(os.getenv("HABR_PAGES_COUNT", 10))

    # ПРОЧИЕ ПАРАМЕТРЫ
    download_delay: int = int(os.getenv("DOWNLOAD_DELAY", 5))
    ua: UserAgent = UserAgent()
    headers: dict | None = None
    utils: Utils = field(default_factory=Utils)

    def __post_init__(self) -> None:
        self.headers = {"User-Agent": self.ua.random}

        # Создание экземпляров класса Fetcher с отдельными
        # параметрами для каждого скрапера
        self.geekjob_fetcher = Fetcher(
            self,
            self.geekjob_url,
            self.geekjob_pages_count,
        )
        self.habr_fetcher = Fetcher(
            self,
            self.habr_url,
            self.habr_pages_count,
        )

        # Создание экземпляров классов скраперов.
        # Всё, что необходимо для добавления нового
        # скрапера - это создать модуль с кодом скрапера
        # в каталоге scrapers и определить здесь его экземпляр.
        self.scrapers = [GeekjobScraper(self), HabrScraper(self)]

    def update_headers(self) -> dict:
        """Обновляет заголовки запроса.

        Метод обновляет значение атрибута `headers` объекта, устанавливая новое
        значение для ключа `User-Agent`. Возвращает обновленный словарь заголовков.

        Returns:
            dict: Обновленный словарь заголовков.

        """
        self.headers = {"User-Agent": self.ua.random}
        return self.headers
