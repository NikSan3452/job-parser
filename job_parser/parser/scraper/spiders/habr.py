import pytz
import scrapy
from dateutil.parser import parse
from scrapy_splash import SplashRequest
from items import VacancyItem
from logger import setup_logging, logger

# Логирование
setup_logging()


class HabrSpider(scrapy.Spider):
    name = "habr"
    allowed_domains = ["career.habr.com"]
    pages_count = 0

    @logger.catch(message="Ошибка в методе HabrSpider.start_requests()")
    def start_requests(self):
        yield SplashRequest(
            url="https://career.habr.com/vacancies", callback=self.parse_vacancy_count
        )

    def parse_vacancy_count(self, response):
        search_total = response.css(".search-total::text").get()
        for string in search_total.split():
            if string.isdigit():
                
                self.pages_count = int(int(string) / 25)

        for page in range(self.pages_count):
            url = f"https://career.habr.com/vacancies?page={page}&type=all"
            yield SplashRequest(url=url, callback=self.parse_pages)

    def parse_pages(self, response):
        for href in response.css('.vacancy-card__title-link::attr("href")').extract():
            url = response.urljoin(href)

            yield SplashRequest(url, callback=self.parse)

    def parse(self, response, **kwargs):
        item = VacancyItem()

        item["job_board"] = "Habr career"
        item["url"] = response.url
        item["title"] = response.css(".page-title__title::text").extract_first("").strip()
        item["city"] = response.xpath("//a[contains(@href, '/vacancies?city_id')]//text()").get()
        item["description"] = response.xpath(
            '//div[@class="vacancy-description__text"]//text()'
        ).getall()
        item["salary"] = response.css(".basic-salary::text").get("Не указана")
        item["company"] = response.css(".company_name a::text").get()
        item["experience"] = response.xpath("//a[contains(@href, '/vacancies?qid')]//text()").get()
        item["type_of_work"] = response.css(
            'span:contains("Полный рабочий день")::text, span:contains("Неполный рабочий день")::text, span:contains("Можно удалённо")::text'
        ).extract()
        item["published_at"] = parse(response.css(".basic-date::attr(datetime)").get()).replace(
            tzinfo=pytz.UTC
        )

        yield item
