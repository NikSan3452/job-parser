import asyncio
import inspect
from parser.scraping.configuration import Config
from typing import AsyncGenerator

import aiohttp
from bs4 import BeautifulSoup
from logger import logger, setup_logging

setup_logging()

config = Config()


class Fetcher:
    """
    Класс Fetcher используется для получения данных с указанного URL и
    выполнения различных задач.

    Attributes:
        url (str): URL-адрес для получения данных
        session (aiohttp.ClientSession): Сессия aiohttp для выполнения запросов
        pages (int): Количество страниц для получения
    """

    def __init__(self, url: str, pages: int, session: aiohttp.ClientSession) -> None:
        """
        Инициализация класса Fetcher.

        При инициализации класса сохраняются переданные аргументы
        в соответствующие атрибуты класса.

        Args:
            url (str): URL-адрес для получения данных
            session (aiohttp.ClientSession): Сессия aiohttp для выполнения запросов
            pages (int): Количество страниц
        """
        self.url = url
        self.session = session
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
        Затем выполняется GET-запрос с использованием асинхронного
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
            headers.update(config.update_headers())  # fake-user-agent
            async with self.session.get(
                url, params=params, headers=headers
            ) as response:
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

        caller_name = inspect.stack()[2].function  # Получаем имя вызывающей функции
        logger.debug(f"Вызывающая функция {caller_name} запустила: {len(tasks)} задач")

        return await asyncio.gather(*tasks)

    async def fetch_vacancy_links(self, board: str) -> list[str]:
        """
        Асинхронный метод для получения ссылок на вакансии с указанной площадки.

        В этом методе сначала вызывается метод `self.fetch_pagination_pages()` 
        для получения данных со всех страниц пагинации. 
        Затем создается пустой список ссылок.

        Далее выполняется цикл по всем полученным страницам пагинации. 
        Для каждой страницы создается объект `BeautifulSoup` для парсинга 
        HTML-кода страницы. 
        Затем выполняется проверка значения аргумента `board` и в зависимости 
        от его значения выполняется поиск ссылок на вакансии на странице 
        с использованием метода `find_all` объекта `BeautifulSoup`. 
        Найденные ссылки добавляются в список ссылок.

        После завершения цикла в лог записывается информация о количестве 
        собранных ссылок. 
        В конце метода возвращается список собранных ссылок.

        Args:
            board (str): Название доски объявлений

        Returns:
            list[str]: Список ссылок на вакансии.
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
        return links

    async def fetch_vacancy_pages(self, links: list[str]) -> AsyncGenerator:
        """
        Асинхронный метод для получения данных со всех страниц вакансий.

        В этом методе создается пустой список задач. 
        Затем выполняется цикл по всем переданным ссылкам на вакансии. 
        Для каждой ссылки выполняется ожидание с задержкой, заданной в конфигурации 
        `config.DOWNLOAD_DELAY`, и создается задача на получение данных со страницы 
        вакансии с помощью вызова метода `self.fetch(link)`. 
        Созданная задача добавляется в список задач.

        После завершения цикла выполняется цикл по всем задачам с использованием функции
        `asyncio.as_completed(tasks)`. 
        Внутри цикла выполняется ожидание завершения текущей задачи 
        и получение результата выполнения задачи. 
        Если результат выполнения задачи является кортежем, то он разбивается 
        на текст ответа и URL-адрес. 
        Если текст ответа или URL-адрес равны None, то выполнение текущей итерации 
        цикла прерывается. 
        В конце каждой итерации цикла с помощью оператора `yield` возвращается 
        кортеж с текстом ответа и URL-адресом.

        Args:
            links (list[str]): Список ссылок на вакансии

        Returns:
            AsyncGenerator: Асинхронный генератор, который возвращает кортежи 
            с текстом ответа и URL-адресом для каждой страницы вакансии.
        """
        tasks: list[asyncio.Future] = []

        for link in links:
            await asyncio.sleep(config.DOWNLOAD_DELAY)
            task = asyncio.create_task(self.fetch(link))
            tasks.append(task)

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
