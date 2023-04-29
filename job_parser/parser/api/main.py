import asyncio
import datetime
import time
from parser.api.base_parser import Parser
from parser.api.config import RequestConfig
from parser.api.parsers import Headhunter, SuperJob, Trudvsem, Zarplata
from parser.api.utils import Utils

from logger import logger, setup_logging

# Логирование
setup_logging()

utils = Utils()


class JobParser:
    """Класс для парсинга вакансий с различных сайтов."""

    def __init__(self, form_params: dict | None) -> None:
        """
        Инициализация экземпляра класса JobParser.

        Attributes:
            city (str | None): Город для поиска вакансий.
            city_from_db (int | None): Идентификатор города из базы данных.
            job (str): Название вакансии для поиска.
            date_from (str | datetime.date | None): Дата начала поиска вакансий.
            date_to (str | datetime.date | None): Дата окончания поиска вакансий.
            title_search (bool): Флаг для поиска по заголовкам вакансий
            experience (int): Опыт работы для поиска вакансий.
            remote (bool): Флаг для поиска удаленных вакансий.
            job_board (str): Название сайта для парсинга вакансий.
            params (RequestConfig): Параметры запроса.
            hh (Headhunter): Экземпляр класса Headhunter.
            sj (SuperJob): Экземпляр класса SuperJob.
            zp (Zarplata): Экземпляр класса Zarplata.
            tv (Trudvsem): Экземпляр класса Trudvsem.

        Args:
            form_params (dict | None): Словарь с параметрами формы. Если не указано,
                используются значения по умолчанию.
        """
        if form_params is None:
            form_params = {}
        self.city: str | None = form_params.get("city", None)
        self.city_from_db: int | None = form_params.get("city_from_db", None)
        self.job: str = form_params.get("job", "Python")
        self.date_to: str | datetime.date | None = form_params.get("date_to")
        self.date_from: str | datetime.date | None = form_params.get("date_from")
        self.title_search: bool = form_params.get("title_search", False)
        self.experience: int = form_params.get("experience", 0)
        self.remote: bool = form_params.get("remote", False)
        self.job_board: str = form_params.get("job_board", "Не имеет значения")

        self.params = RequestConfig(
            city=self.city,
            city_from_db=self.city_from_db,
            job=self.job,
            date_from=self.date_from,
            date_to=self.date_to,
            remote=self.remote,
            experience=self.experience,
        )
        self.hh = Headhunter(self.params)
        self.sj = SuperJob(self.params)
        self.zp = Zarplata(self.params)
        self.tv = Trudvsem(self.params)

    async def parse_vacancies(self) -> None:
        """
        Асинхронный метод для парсинга вакансий.

        Метод вызывает соответствующие методы парсинга в зависимости от значения
        атрибута job_board. Если значение равно "Не имеет значения", то вызываются
        методы парсинга для всех сайтов. Иначе вызывается метод парсинга для указанного
        сайта.
        """
        Parser.general_job_list.clear()
        if self.job_board == "Не имеет значения":
            await self.parse_all_vacancies()
        else:
            await self.parse_vacancies_by_job_board()

    async def parse_vacancies_by_job_board(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с указанного сайта.

        Метод вызывает соответствующий метод парсинга в зависимости от значения
        атрибута job_board.

        """
        match self.job_board:
            case "HeadHunter":
                await self.hh.parsing_vacancy_headhunter()
            case "SuperJob":
                await self.sj.parsing_vacancy_superjob()
            case "Zarplata":
                await self.zp.parsing_vacancy_zarplata()
            case "Trudvsem":
                await self.tv.parsing_vacancy_trudvsem()

    async def parse_all_vacancies(self) -> None:
        """
        Асинхронный метод для парсинга вакансий со всех сайтов.

        Метод создает задачи для парсинга вакансий с каждого сайта и ожидает
        их выполнения.
        """
        task1 = asyncio.create_task(self.hh.parsing_vacancy_headhunter())
        task2 = asyncio.create_task(self.sj.parsing_vacancy_superjob())
        task3 = asyncio.create_task(self.zp.parsing_vacancy_zarplata())
        task4 = asyncio.create_task(self.tv.parsing_vacancy_trudvsem())

        await asyncio.gather(task1, task2, task3, task4)

    async def sort_vacancy_list(self) -> list[dict]:
        """
        Асинхронный метод для сортировки списка вакансий.

        Метод сортирует список вакансий по дате и, если указано,
        по названию и удаленной работе.
        Возвращает отсортированный список вакансий.

        Returns:
            list[dict]: Отсортированный список вакансий.
        """
        sorted_list = await utils.sort_by_date(Parser.general_job_list)

        if self.title_search:
            sorted_list = await utils.sort_by_title(sorted_list, self.job)

        if self.remote:
            sorted_list = await utils.sort_by_remote_work(sorted_list)

        if self.remote and self.title_search:
            sorted_list_by_title = await utils.sort_by_title(sorted_list, self.job)
            sorted_list = await utils.sort_by_remote_work(sorted_list_by_title)

        return sorted_list


async def run(form_params: dict = None) -> list[dict]:
    """
    Асинхронная функция для запуска парсинга вакансий.

    Функция создает экземпляр класса JobParser с указанными параметрами формы,
    вызывает методы парсинга и сортировки и возвращает отсортированный список вакансий.

    Args:
        form_params (dict | None): Словарь с параметрами формы. Если не указано,
            используются значения по умолчанию.

    Returns:
        list[dict]: Отсортированный список вакансий.
    """
    start = time.time()
    parser = JobParser(form_params)

    await parser.parse_vacancies()

    sorted_job_list = await parser.sort_vacancy_list()

    end = time.time() - start
    logger.debug(f"Количество вакансий: {len(sorted_job_list)}")
    logger.debug(f"Время затраченное на сбор: {round(end, 2)}")

    return sorted_job_list
