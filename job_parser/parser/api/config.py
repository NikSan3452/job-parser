import datetime
import os

from dataclasses import dataclass
from typing import Optional


class ParserConfig:
    """Этот класс хранит параметры запросов к API."""

    superjob_domen: str = "https://api.superjob.ru"
    superjob_api_version: str = "2.0"
    superjob_api_path: str = "vacancies"
    superjob_secret_key: str = os.getenv("SUPERJOB_SECRET_KEY")
    superjob_headers: dict = {"x-api-app-id": superjob_secret_key}
    superjob_url: str = f"{superjob_domen}/{superjob_api_version}/{superjob_api_path}/"

    headhunter_domen: str = "https://api.hh.ru"
    headhunter_api_path: str = "vacancies"
    headhunter_url: str = f"{headhunter_domen}/{headhunter_api_path}"

    zarplata_domen: str = "https://api.zarplata.ru"
    zarplata_api_path: str = "vacancies"
    zarplata_url: str = f"{zarplata_domen}/{zarplata_api_path}"


@dataclass
class RequestConfig:
    """Этот класс хранит параметры запроса парсеров."""
    city: Optional[str]
    city_from_db: Optional[int]
    job: Optional[str]
    date_to: Optional[str | datetime.date]
    date_from: Optional[str | datetime.date]
    experience: int
