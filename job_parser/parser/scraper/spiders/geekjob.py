import scrapy

from . import items
from logger import logger, setup_logging

# Логирование
setup_logging()


class GeekjobSpider(scrapy.Spider):
    name = "geekjob"
    allowed_domains = ["geekjob.ru"]
    pages_count = 1

    custom_settings = {
        "ITEM_PIPELINES": {
            "parser.scraper.pipelines.GeekjobPipeline": 400,
        }
    }

    @logger.catch(message="Ошибка в методе GeekjobSpider.start_requests()")
    def start_requests(self):
        yield scrapy.Request(
            url="https://geekjob.ru/vacancies",
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
        search_total = response.css("#paginator > p > strong::text").get()
        if search_total is not None:
            search_total = search_total.replace(" ", "")
            self.pages_count = int(int(search_total) / 20)

        for page in range(self.pages_count + 1):
            url = f"https://geekjob.ru/vacancies/{page}"
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
        for href in response.css('.vacancy-name > .title::attr("href")').extract():
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

        item["job_board"] = "Geekjob"

        item["url"] = response.url

        item["title"] = response.css("header > h1::text").get()

        item["city"] = response.css("header > .location::text").get()

        item["description"] = response.xpath(
            '//div[@id="vacancy-description"]//text()'
        ).getall()

        item["salary"] = response.css(".jobinfo > .salary::text").get("Не указана")

        item["company"] = response.css(".company-name > a::text").get()

        item["experience"] = response.css(".jobinfo > .jobformat::text").getall()[1]

        item["type_of_work"] = response.css(".jobinfo > .jobformat::text").getall()[0]

        item["published_at"] = response.css("header > .time::text").get()

        logger.debug(response.request.headers.get("User-Agent"))

        yield item
