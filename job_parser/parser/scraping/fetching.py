import asyncio
import inspect
from typing import AsyncGenerator
import aiohttp
from bs4 import BeautifulSoup
from parser.scraping.configuration import Config
from logger import setup_logging, logger

setup_logging()

config = Config()


class Fetcher:
    """Класс описывает методы получения данных со страниц"""

    def __init__(self, url: str, session: aiohttp.ClientSession, pages: int) -> None:
        self.url = url
        self.session = session
        self.pages = pages

    async def fetch(
        self,
        url: str,
        params: dict[str, str] = {},
        headers: dict[str, str] = {},
    ) -> tuple[str, str] | None:
        try:
            headers.update(config.update_headers())  # fake-user-agent
            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
                logger.debug(headers)
                logger.debug(f"Status code: {response.status}")
                return await response.text(), str(response.url)
        except Exception as exc:
            return logger.exception(exc)

    async def fetch_pagination_pages(self) -> asyncio.Future[list]:
        """Получает страницы со списками вакансий.
        На каждой странице по 20 ссылок на вакансии.
        Returns:
            asyncio.Future[list]: Список задач.
        """
        tasks: list[asyncio.Future] = []

        for page_num in range(1, self.pages + 1):
            page_url = f"{self.url}{page_num}"
            task = asyncio.create_task(self.fetch(page_url))
            tasks.append(task)

        caller_name = inspect.stack()[2].function  # Получаем имя вызывающей функции
        logger.debug(f"Вызывающая функция {caller_name} запустила: {len(tasks)} задач")

        return await asyncio.gather(*tasks)

    async def fetch_vacancy_links(self, board: str) -> list[str]:
        """Производит выборку всех ссылок на вакансии.
        Args:
            board: str: Площадка.
        Returns:
            list[str]: Список ссылок.
        """
        html_pages = await self.fetch_pagination_pages()
        links: list[str] = []

        for html in html_pages:
            soup = BeautifulSoup(html[0], "lxml")
            match board:
                case "Geekjob":
                    page_links = soup.find_all("a", class_="title")
                    links += [
                        config.GEEKJOB_DOMAIN + link.get("href") for link in page_links
                    ]
                case "Habr":
                    page_links = soup.find_all("a", class_="vacancy-card__title-link")
                    links += [
                        config.HABR_DOMAIN + link.get("href") for link in page_links
                    ]
        logger.debug(f"Собрано ссылок: {len(links)} ")
        return links

    async def fetch_vacancy_pages(self, links: list[str]) -> AsyncGenerator:
        """Производит асинхронный запуск задач
        по выборке данных со страниц вакансий.

        Args:
            links list[str]: Список ссылок на вакансии.

        Returns:
            AsyncGenerator: Список задач.
        """
        tasks: list[asyncio.Future] = []

        for link in links:
            await asyncio.sleep(config.DOWNLOAD_DELAY)
            task = asyncio.create_task(self.fetch(link))
            tasks.append(task)

            logger.debug(f"Идет выборка данных со страницы {link}")

        # Проверяем, что вернет задача, если None то пропускаем,
        # таким образом избавляемся от пустых и некорректных значений в БД
        for task_ in asyncio.as_completed(tasks):
            try:
                text, url = await task_
            except TypeError as exc:
                logger.exception(exc)
            if text is None or url is None:
                continue
            yield (text, url)
