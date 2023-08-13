from parser.parsing.config import ParserConfig

from logger import setup_logging

# Логирование
setup_logging()

config = ParserConfig()


class JobParser:
    """
    Класс содержит методы для парсинга вакансий с различных сайтов.

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
