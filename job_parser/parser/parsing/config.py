import datetime
import os
from dataclasses import dataclass, field
from parser.parsing.connection import WebClient
from parser.parsing.db import Database
from parser.parsing.fetcher import Fetcher
from parser.parsing.parsers.headhunter import Headhunter
from parser.parsing.parsers.superjob import SuperJob
from parser.parsing.parsers.trudvsem import Trudvsem
from parser.parsing.parsers.zarplata import Zarplata
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from fake_useragent import UserAgent

if TYPE_CHECKING:
    from parser.parsing.parsers.base import Parser

from parser.utils import Utils

load_dotenv()


@dataclass
class ParserConfig:
    """Этот класс хранит параметры запросов к API."""

    # HEADHUNTER
    hh_domain: str = "https://api.hh.ru"
    hh_api_path: str = "vacancies"
    hh_url: str = f"{hh_domain}/{hh_api_path}"
    hh_pages: int = 20
    hh_items: str = "items"
    hh_job_board: str = "HeadHunter"
    hh_params: dict = field(default_factory=dict)

    # ZARPLATA
    zp_domain: str = "https://api.zarplata.ru"
    zp_api_path: str = "vacancies"
    zp_url: str = f"{zp_domain}/{zp_api_path}"
    zp_pages: int = 20
    zp_items: str = "items"
    zp_job_board: str = "Zarplata"
    zp_params: dict = field(default_factory=dict)

    # SUPERJOB
    sj_domain: str = "https://api.superjob.ru"
    sj_api_version: str = "2.20"
    sj_api_path: str = "vacancies"
    sj_secret_key: str = os.getenv("SUPERJOB_SECRET_KEY1", "")
    sj_url: str = f"{sj_domain}/{sj_api_version}/{sj_api_path}/"
    sj_pages: int = 5
    sj_items: str = "objects"
    sj_job_board: str = "SuperJob"
    sj_params: dict = field(default_factory=dict)

    # TRUDVSEM
    tv_domain: str = "http://opendata.trudvsem.ru/api"
    tv_version: str = "v1"
    tv_api_path: str = "vacancies"
    tv_url: str = f"{tv_domain}/{tv_version}/{tv_api_path}"
    tv_job_board: str = "Trudvsem"
    tv_pages: int = 20
    tv_items: str = "results"

    # OTHERS
    ua: UserAgent = UserAgent()
    delay: float = 0.2

    def __post_init__(self) -> None:
        self.client = WebClient(self)
        self.db = Database()
        self.utils = Utils()

        self.hh_params.update(
            {
                "per_page": 100,
                "date_from": datetime.date.today(),
                "date_to": datetime.date.today(),
            }
        )
        self.zp_params.update(
            {
                "per_page": 100,
                "date_from": datetime.date.today(),
                "date_to": datetime.date.today(),
            }
        )
        self.sj_params.update(
            {
                "count": 100,
                "date_published_from": self.utils.get_sj_date_from(),
                "date_published_to": self.utils.get_sj_date_to(),
            }
        )
        self.tv_params = {
            "limit": 100,
            "offset": 0,
            "modifiedFrom": self.utils.get_tv_date_from(),
            "modifiedTo": self.utils.get_tv_date_to(),
        }

        self.hh_fetcher = Fetcher(
            self.hh_job_board,
            self.hh_url,
            self.hh_params,
            self.hh_pages,
            self.hh_items,
            self.client,
        )

        self.zp_fetcher = Fetcher(
            self.zp_job_board,
            self.zp_url,
            self.zp_params,
            self.zp_pages,
            self.zp_items,
            self.client,
        )

        self.sj_fetcher = Fetcher(
            self.sj_job_board,
            self.sj_url,
            self.sj_params,
            self.sj_pages,
            self.sj_items,
            self.client,
        )

        self.tv_fetcher = Fetcher(
            self.tv_job_board,
            self.tv_url,
            self.tv_params,
            self.tv_pages,
            self.tv_items,
            self.client,
        )

        self.hh_parser = Headhunter(self)
        self.zp_parser = Zarplata(self)
        self.sj_parser = SuperJob(self)
        self.tv_parser = Trudvsem(self)

        self.parsers: list["Parser"] = [
            self.hh_parser,
            self.zp_parser,
            self.sj_parser,
            self.tv_parser,
        ]

    def update_headers(self, url: str) -> dict:
        """
        Метод для обновления заголовков запроса.

        Метод принимает на вход URL и возвращает словарь с заголовками запроса.
        Метод создает пустой словарь `headers`, затем проверяет, равен ли переданный URL
        значению атрибута `sj_url`. Если это так, то в словарь `headers` добавляется
        пара ключ-значение, где ключ равен "x-api-app-id", а значение выбирается
        случайным образом из списка секретных ключей (атрибут `sj_secret_keys_list`).
        В конце работы метода возвращается словарь с заголовками запроса.

        Args:
            url (str): URL для обновления заголовков запроса.

        Returns:
            dict: Словарь с заголовками запроса.
        """
        headers = {}
        # headers.update({"User-Agent": self.ua.random})
        if url == self.sj_url:
            headers.update({"x-api-app-id": self.sj_secret_key})
        return headers
