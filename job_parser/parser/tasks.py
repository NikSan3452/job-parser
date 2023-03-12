import asyncio
import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

from logger import logger, setup_logging
from parser.scraper.spiders.habr import HabrSpider
from parser.scraper.spiders.geekjob import GeekjobSpider
from profiles.models import Profile
from scrapy.crawler import CrawlerProcess
from dataclasses import asdict, dataclass, field

from job_parser.celery import app
from .api import main
from .models import VacancyScraper

setup_logging()


@app.task
def sending_emails() -> None:
    """Отвечает за рассылку электронных писем с вакансиями"""
    try:
        # Выбираем из БД тех пользователей, у которых покдлючена подписка
        profiles = Profile.objects.filter(subscribe=True)
        logger.debug("Профили получены")
        for profile in profiles:

            # Выбираем из БД вакансии для конкретного пользователя за сегодня
            job_list_from_scraper = VacancyScraper.objects.filter(
                title=profile.job,
                city=profile.city,
                published_at=datetime.date.today(),
            )
            logger.debug("Вакансии со скрапера получены")

            job_list_from_api = asyncio.run(main.run())
            logger.debug("Вакансии с api получены")

            for job in job_list_from_scraper:
                job_list_from_api.append(job)

            # Формируем письмо
            subject = f"Вакансии по вашим предпочтениям за {datetime.date.today()}"
            text_content = "Рассылка вакансий"
            from_email = settings.EMAIL_HOST_USER
            html = ""
            empty = "<h2>К сожалению на сегодня вакансий нет.</h2>"

            # Итерируем по списку вакансий и формируем html документ
            for vacancy in job_list_from_api:
                html += f'<h5><a href="{vacancy.get("url")}">{vacancy.get("title")}</a></h5>'
                html += f'<p>{vacancy.get("company")}</p>'
                html += f'<p>Город: {vacancy.get("city")} | Дата публикации: {vacancy.get("published_at")}</p>'

            # Если вакансий нет, придет сообщение о том, что вакансий на сегодня не нашлось
            _html = html if html else empty

            to = profile.user.email  # Получаем email из модели User
            try:
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
                msg.attach_alternative(_html, "text/html")
                msg.send()
                logger.debug(f"Письмо на адрес {to} отправлено")
            except Exception as exc:
                logger.exception(exc)

    except Exception as exc:
        logger.exception(exc)


@dataclass
class ScraperSettings:
    TWISTED_REACTOR: str = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    DOWNLOAD_HANDLERS: dict = field(
        default_factory=lambda: {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        }
    )
    PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT: int = 300000
    REQUEST_FINGERPRINTER_IMPLEMENTATION: str = "2.7"
    FAKEUSERAGENT_PROVIDERS: list = field(
        default_factory=lambda: [
            "scrapy_fake_useragent.providers.FakeUserAgentProvider",
            "scrapy_fake_useragent.providers.FakerProvider",
            "scrapy_fake_useragent.providers.FixedUserAgentProvider",
        ],
    )
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    DOWNLOADER_MIDDLEWARES: dict = field(
        default_factory=lambda: {
            "parser.scraper.middlewares.ScraperDownloaderMiddleware": 543,
            "scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware": 810,
            "scrapy.downloadermiddlewares.useragent.UserAgentMiddleware": None,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "scrapy_fake_useragent.middleware.RandomUserAgentMiddleware": 400,
            "scrapy_fake_useragent.middleware.RetryUserAgentMiddleware": 401,
        },
    )
    SPIDER_MIDDLEWARES: dict = field(
        default_factory=lambda: {
            "parser.scraper.middlewares.ScraperSpiderMiddleware": 543,
        },
    )
    COOKIES_ENABLED: bool = False


class ScraperCelery:
    def __init__(self, scraper_settings: ScraperSettings) -> None:
        self.scraper_settings = scraper_settings
        self.process = CrawlerProcess(asdict(self.scraper_settings))

    def run_spiders(self) -> None:
        """Отвечает за запуск пауков"""

        # Добавляем пауков в процесс
        self.process.crawl(HabrSpider)
        self.process.crawl(GeekjobSpider)

        # Запуск
        self.process.start(stop_after_crawl=False)

    def delete_old_vacancies(self):
        """Удаляет вакансии старше 10 дней."""
        min_date = datetime.datetime.today() - datetime.timedelta(days=10)
        VacancyScraper.objects.filter(published_at__lte=min_date).delete()


scraper_settings = ScraperSettings()
scraper = ScraperCelery(scraper_settings)


@app.task
def run_scraper() -> None:
    """Запуск скрапера."""
    scraper.run_spiders()


@app.task
def run_delete_old_vacancies():
    """Запуск удаления старых вакансий"""
    scraper.delete_old_vacancies()
