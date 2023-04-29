import datetime
import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ParserConfig:
    """Этот класс хранит параметры запросов к API."""

    superjob_domain: str = "https://api.superjob.ru"
    superjob_api_version: str = "2.0"
    superjob_api_path: str = "vacancies"
    superjob_secret_keys_list: list[str] = [
        os.getenv("SUPERJOB_SECRET_KEY1"),
        os.getenv("SUPERJOB_SECRET_KEY2"),
        os.getenv("SUPERJOB_SECRET_KEY3"),
    ]
    superjob_url: str = f"{superjob_domain}/{superjob_api_version}/{superjob_api_path}/"

    headhunter_domain: str = "https://api.hh.ru"
    headhunter_api_path: str = "vacancies"
    headhunter_url: str = f"{headhunter_domain}/{headhunter_api_path}"

    zarplata_domain: str = "https://api.zarplata.ru"
    zarplata_api_path: str = "vacancies"
    zarplata_url: str = f"{zarplata_domain}/{zarplata_api_path}"

    trudvsem_domain: str = "http://opendata.trudvsem.ru/api"
    trudvsem_version: str = "v1"
    trudvsem_api_path: str = "vacancies"
    trudvsem_url: str = f"{trudvsem_domain}/{trudvsem_version}/{trudvsem_api_path}"


@dataclass
class RequestConfig:
    """Этот класс хранит параметры запроса парсеров."""

    city: str | None
    city_from_db: int | None
    job: str | None
    date_to: str | datetime.date | None
    date_from: str | datetime.date | None
    remote: bool
    experience: int
