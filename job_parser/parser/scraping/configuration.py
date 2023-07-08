from dataclasses import dataclass
import os

from fake_useragent import UserAgent


@dataclass
class Config:
    """Класс описывает конфигурацию парсеров."""
    # GEEKJOB
    geekjob_domain: str = "https://geekjob.ru"
    geekjob_uri: str = "vacancies"
    geekjob_url: str = f"{geekjob_domain}/{geekjob_uri}/"
    geekjob_job_board: str = "Geekjob"
    geekjob_pages_count: int = int(os.getenv("GEEKJOB_PAGES_COUNT", 5))

    #HABR
    habr_domain: str = "https://career.habr.com"
    habr_uri: str = "vacancies?sort=date&type=all&page="
    habr_url: str = f"{habr_domain}/{habr_uri}"
    habr_job_board: str = "Habr"
    habr_pages_count: int = int(os.getenv("HABR_PAGES_COUNT", 10))

    download_delay: int = int(os.getenv("DOWNLOAD_DELAY", 5))

    ua: UserAgent = UserAgent()
    headers: dict | None = None

    def __post_init__(self) -> dict:
        self.headers = {"User-Agent": self.ua.random}
        return self.headers

    def update_headers(self) -> dict:
        """Обновляет заголовки запроса.

        Метод обновляет значение атрибута `headers` объекта, устанавливая новое
        значение для ключа `User-Agent`. Возвращает обновленный словарь заголовков.

        Returns:
            dict: Обновленный словарь заголовков.

        """
        self.headers = {"User-Agent": self.ua.random}
        return self.headers