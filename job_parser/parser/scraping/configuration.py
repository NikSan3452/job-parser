from dataclasses import dataclass
from django.conf import settings
from fake_useragent import UserAgent


@dataclass
class Config:
    """Класс описывает конфигурацию парсеров."""

    GEEKJOB_DOMAIN: str = "https://geekjob.ru"
    GEEKJOB_URI: str = "vacancies"
    GEEKJOB_URL: str = f"{GEEKJOB_DOMAIN}/{GEEKJOB_URI}/"

    HABR_DOMAIN: str = "https://career.habr.com"
    HABR_URI: str = "vacancies?sort=date&type=all&page="
    HABR_URL: str = f"{HABR_DOMAIN}/{HABR_URI}"

    DOWNLOAD_DELAY: int = int(settings.DOWNLOAD_DELAY)

    GEEKJOB_PAGES_COUNT: int = int(settings.GEEKJOB_PAGES_COUNT)
    HABR_PAGES_COUNT: int = int(settings.HABR_PAGES_COUNT)

    ua: UserAgent = UserAgent()
    headers: dict | None = None

    def __post_init__(self):
        self.headers = {"User-Agent": self.ua.random}

    def update_headers(self):
        self.headers = {"User-Agent": self.ua.random}
        return self.headers
