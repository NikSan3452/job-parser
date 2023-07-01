from dataclasses import dataclass
from django.conf import settings
from fake_useragent import UserAgent


@dataclass
class Config:
    """Класс описывает конфигурацию парсеров."""

    GEEKJOB_DOMAIN: str = "https://geekjob.ru"
    GEEKJOB_URI: str = "vacancies"
    GEEKJOB_URL: str = f"{GEEKJOB_DOMAIN}/{GEEKJOB_URI}/"
    geekjob_job_board: str = "Geekjob"

    HABR_DOMAIN: str = "https://career.habr.com"
    HABR_URI: str = "vacancies?sort=date&type=all&page="
    HABR_URL: str = f"{HABR_DOMAIN}/{HABR_URI}"
    habr_job_board: str = "Habr"

    DOWNLOAD_DELAY: int = int(settings.DOWNLOAD_DELAY)

    GEEKJOB_PAGES_COUNT: int = int(settings.GEEKJOB_PAGES_COUNT)
    HABR_PAGES_COUNT: int = int(settings.HABR_PAGES_COUNT)

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