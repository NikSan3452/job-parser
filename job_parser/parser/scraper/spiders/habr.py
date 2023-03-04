import pytz
import scrapy
from dateutil.parser import parse

from . import items
from logger import logger, setup_logging

# Логирование
setup_logging()


class HabrSpider(scrapy.Spider):
    name = "habr"
    allowed_domains = ["career.habr.com"]
    pages_count = 1

    @logger.catch(message="Ошибка в методе HabrSpider.start_requests()")
    def start_requests(self):
        yield scrapy.Request(
            url="https://career.habr.com/vacancies",
            callback=self.parse_vacancy_count,
            meta=dict(playwright=True),
        )

    def parse_vacancy_count(self, response):
        """Находит общее количество страниц и итерирует по ним в этом диапазоне.

        Args:
            response (_type_): Ответ.

        Yields:
            _type_: Генератор с коллбеком следующей функции.
        """
        # Получаем общее количество страниц
        search_total = response.css(".search-total::text").get()
        if search_total is not None:
            for string in search_total.split():
                if string.isdigit():
                    self.pages_count = int(int(string) / 25)

        for page in range(self.pages_count + 1):
            url = f"https://career.habr.com/vacancies?sort=date&page={page}&type=all"
            if page >= self.pages_count + 1:
                logger.debug("Парсинг страниц окончен")
            yield scrapy.Request(url=url, callback=self.parse_pages)

    def parse_pages(self, response):
        """Извлекает адрес очередной страницы.

        Args:
            response (_type_): Ответ.

        Yields:
            _type_: Генератор с коллбеком следующей функции.
        """
        for href in response.css('.vacancy-card__title-link::attr("href")').extract():
            url = response.urljoin(href)

            yield scrapy.Request(url, callback=self.parse)

    def parse(self, response, **kwargs):
        """Парсит очередную страницу.

        Args:
            response (_type_): Ответ.

        Yields:
            _type_: Объект ссодержащий атрибуты, которые были спарсены.
        """
        item = items.VacancyItem()

        item["job_board"] = "Habr career"

        item["url"] = response.url

        item["title"] = (
            response.css(".page-title__title::text").extract_first("").strip()
        )

        item["city"] = response.xpath(
            "//a[contains(@href, '/vacancies?city_id')]//text()"
        ).get()

        item["description"] = response.xpath(
            '//div[@class="vacancy-description__text"]//text()'
        ).getall()

        item["salary"] = response.css(".basic-salary::text").get("Не указана")

        item["company"] = response.css(".company_name a::text").get()

        item["experience"] = response.xpath(
            "//a[contains(@href, '/vacancies?qid')]//text()"
        ).get()

        item["type_of_work"] = response.css(
            "div.content-section span.inline-list span::text"
        ).re(r"Полный рабочий день|Неполный рабочий день|Можно удал[её]нно")

        item["published_at"] = parse(
            response.css(".basic-date::attr(datetime)").get()
        ).replace(tzinfo=pytz.UTC)

        logger.debug(response.request.headers.get("User-Agent"))

        yield item
