from parser.parsing.config import ParserConfig

from logger import setup_logging

# Логирование
setup_logging()

config = ParserConfig()


class JobParser:
    """
    Класс для парсинга вакансий.

    Класс содержит методы для парсинга вакансий с различных сайтов. При инициализации
    объекта класса создаются объекты классов `Headhunter`, `SuperJob`, `Zarplata`
    и `Trudvsem`, которые используются для парсинга вакансий с соответствующих сайтов.

    Attributes:
        (Headhunter): Объект класса `Headhunter` для парсинга вакансий с сайта
        HeadHunter.
        (SuperJob): Объект класса `SuperJob` для парсинга вакансий с сайта SuperJob.
        (Zarplata): Объект класса `Zarplata` для парсинга вакансий с сайта Zarplata.
        (Trudvsem): Объект класса `Trudvsem` для парсинга вакансий с сайта Trudvsem.
    """
    @config.utils.timeit
    async def parse_headhunter(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с сайта headhunter.

        Returns:
            None
        """
        await config.hh_parser.parse()

    @config.utils.timeit
    async def parse_zarplata(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с сайта zarplata.

        Returns:
            None
        """
        await config.zp_parser.parse()

    @config.utils.timeit
    async def parse_superjob(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с сайта superjob.

        Returns:
            None
        """
        await config.sj_parser.parse()

    @config.utils.timeit
    async def parse_trudvsem(self) -> None:
        """
        Асинхронный метод для парсинга вакансий с сайта trudvsem.

        Returns:
            None
        """
        await config.tv_parser.parse()
