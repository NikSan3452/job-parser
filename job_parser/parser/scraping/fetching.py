import asyncio
from typing import TYPE_CHECKING

import aiohttp
from bs4 import BeautifulSoup
from logger import logger, setup_logging

if TYPE_CHECKING:
    from parser.scraping.configuration import Config

setup_logging()


class Fetcher:
    """
    Класс Fetcher используется для получения данных с указанного URL.

    Attributes:
        config (Config): Экземпляр класса конфигурации.
        url (str): URL-адрес для получения данных
        pages (int): Количество страниц для получения
    """

    def __init__(self, config: "Config", url: str, pages: int) -> None:
        self.config = config
        self.url = url
        self.pages = pages

    async def fetch(
        self,
        url: str,
        params: dict[str, str] = {},
        headers: dict[str, str] = {},
    ) -> tuple[str, str] | None:
        """
        Асинхронный метод для получения данных с указанного URL.

        В этом методе выполняется GET-запрос к указанному URL с переданными
        параметрами и заголовками.
        Перед отправкой запроса заголовки обновляются рандомным фейковым user-agent
        с помощью вызова функции `config.update_headers()`.
        Далее создается сессия и выполняется GET-запрос с использованием асинхронного
        контекстного менеджера.
        После получения ответа в лог записывается информация о заголовках
        и коде состояния ответа.
        В конце метода возвращается кортеж с текстом ответа и URL-адресом.

        В случае возникновения исключения информация об исключении
        записывается в лог и возвращается None.

        Args:
            url (str): URL-адрес для получения данных
            params (dict[str, str], optional): Параметры запроса.
            По умолчанию пустой словарь.
            headers (dict[str, str], optional): Заголовки запроса.
            По умолчанию пустой словарь.

        Returns:
            tuple[str, str] | None: Кортеж с текстом ответа и URL-адресом
            или None в случае ошибки.
        """
        try:
            headers.update(self.config.update_headers())  # fake-user-agent
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params=params,
                    headers=headers,
                ) as response:
                    if not response.status == 200:
                        logger.debug(f"Error, response status code {response.status}")
                    return await response.text(), str(response.url)
        except Exception as exc:
            return logger.exception(exc)

    async def fetch_pagination_pages(self) -> asyncio.Future[list]:
        """
        Асинхронный метод для получения данных со всех страниц пагинации.

        В этом методе создается пустой список задач.
        Затем выполняется цикл по всем страницам пагинации.
        Для каждой страницы формируется URL-адрес страницы пагинации
        и создается задача на получение данных с помощью вызова метода
        `self.fetch(page_url)`.
        Созданная задача добавляется в список задач.

        После завершения цикла в лог записывается информация о вызывающей функции
        и количестве созданных этой функцией задач.
        Затем выполняется ожидание завершения всех задач с помощью вызова
        `await asyncio.gather(*tasks)` и возвращается список с результатами
        их выполнения.

        Returns:
            asyncio.Future[list]: Список с данными со всех страниц пагинации.
        """
        tasks: list[asyncio.Future] = []

        for page_num in range(1, self.pages + 1):
            page_url = f"{self.url}{page_num}"
            task = asyncio.create_task(self.fetch(page_url))
            tasks.append(task)

        return await asyncio.gather(*tasks)

    async def fetch_vacancy_pages(self, links: list[str]) -> list[tuple[str, str]]:
        """
        Асинхронный метод для получения страниц вакансий.

        В этом методе создается список задач для асинхронного скачивания страниц
        вакансий по указанным ссылкам. Затем выполняется ожидание завершения всех
        задач и сбор результатов.

        В случае возникновения исключения при выполнении задачи, оно логируется,
        а результат игнорируется.

        Args:
            links (list[str]): Список ссылок на страницы вакансий.
        Returns:
            list[tuple[str, str]]: Список кортежей с HTML-кодом страницы и URL-адресом.
        """
        tasks: list[asyncio.Future] = []
        results: list[tuple[str, str]] = []

        for link in links:
            await asyncio.sleep(self.config.download_delay)
            task = asyncio.create_task(self.fetch(link))
            tasks.append(task)
        for task_ in asyncio.as_completed(tasks):
            try:
                text, url = await task_
            except Exception as exc:
                logger.exception(exc)
            if text is None or url is None:
                continue
            results.append((text, url))
        return results

    async def get_vacancy_links(
        self, domain: str, selector: str | None = None, tag: str | None = None
    ) -> list[str]:
        """
        Асинхронный метод для получения ссылок на вакансии с указанной площадки.

        Args:
            domain (str): Домен сайта.
            selector (str | None ): Название html-класса, по которому будет
            осуществлен поиск.
            tag: (str | None ): HTML-тег.
        Returns:
            list[str]: Список ссылок на вакансии.
        """
        html_pages = await self.fetch_pagination_pages()
        links: list[str] = []

        for html in html_pages:
            soup = BeautifulSoup(html[0], "lxml")
            if tag:
                page_links = soup.find_all(name=tag)
            if selector:
                page_links = soup.find_all("a", class_=selector)
            for link in page_links:
                href = link.get("href")
                if href.startswith("http") or href.startswith("https"):
                    links.append(href)
                else:
                    links.append(domain + href)
        return links
