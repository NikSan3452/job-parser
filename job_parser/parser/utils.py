import asyncio
import datetime
import json
import time
from functools import wraps

from django.http import HttpRequest
from logger import logger, setup_logging

setup_logging()


class Utils:
    @staticmethod
    def check_date_from(
        date_from: str | None | datetime.datetime,
    ) -> datetime.datetime | str:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str | None | datetime.datetime): Дата от.

        Returns:
            datetime.datetime | str: Время задаваемое по
            умолчанию.
        """
        if not date_from or date_from == "":
            new_date_from = datetime.datetime.today().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        elif isinstance(date_from, str):
            new_date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d").replace(
                hour=0, minute=0, second=0, microsecond=0
            )
        else:
            new_date_from = date_from.replace(hour=0, minute=0, second=0, microsecond=0)
        return new_date_from

    @staticmethod
    def check_date_to(
        date_to: str | None | datetime.datetime,
    ) -> datetime.datetime | str:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_to (str | None | datetime.datetime): Дата до.

        Returns:
            datetime.datetime | str: Время задаваемое по
            умолчанию.
        """
        if not date_to or date_to == "":
            new_date_to = datetime.datetime.today().replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        elif isinstance(date_to, str):
            new_date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d").replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        else:
            new_date_to = date_to.replace(
                hour=23, minute=59, second=59, microsecond=999999
            )
        return new_date_to

    @staticmethod
    def convert_experience(experience: int, job_board: str) -> str:
        """
        Статический метод для преобразования опыта работы.

        Метод принимает на вход целое число с опытом работы и строку с названием сайта
        для поиска работы и возвращает строку с преобразованным опытом работы.
        Метод проверяет значение аргумента `job_board`. Если значение равно "SuperJob",
        то метод использует оператор `match` для сопоставления значения аргумента
        `experience` с различными вариантами и возвращает соответствующую строку.
        Если значение аргумента `job_board` равно "Trudvsem", то метод также использует
        оператор `match` для сопоставления значения аргумента `experience` с различными
        вариантами и возвращает соответствующую строку.

        Args:
            experience (int): Целое число с опытом работы.
            job_board (str): Строка с названием сайта для поиска работы.

        Returns:
            str: Строка с преобразованным опытом работы.
        """
        if job_board == "SuperJob":
            match experience:
                case 0 | 1:
                    converted_experience = "Нет опыта"
                case 2:
                    converted_experience = "От 1 года до 3 лет"
                case 3:
                    converted_experience = "От 3 до 6 лет"
                case 4:
                    converted_experience = "От 6 лет"
        elif job_board == "Trudvsem":
            match experience:
                case 0:
                    converted_experience = "Нет опыта"
                case 1 | 2 | 3:
                    converted_experience = "От 1 года до 3 лет"
                case 4 | 5 | 6:
                    converted_experience = "От 3 до 6 лет"
                case _ if experience > 6:
                    converted_experience = "От 6 лет"

        return converted_experience

    @staticmethod
    def convert_currency(currency: str) -> str | None:
        """Конвертирует символ или код валюты в код валюты.

        Этот метод принимает на вход символ или код валюты и возвращает соответствующий
        код валюты. Если валюта не найдена, метод возвращает None.

        Создается словарь `currencies`, где ключи - это названия валют,
        а значения - это списки с кодами и символами валют. Входная строка
        приводится к нижнему регистру. Происходит перебор всех элементов
        словаря `currencies`. Для каждого элемента словаря происходит перебор
        всех символов и кодов валют. Если символ или код валюты совпадает с
        входной строкой, то метод возвращает соответствующий код валюты.
        Если ни один символ или код валюты не совпадает с входной строкой,
        то метод возвращает None.

        Args:
            currency (str): Символ или код валюты для поиска.

        Returns:
            str | None: Код валюты, если он найден, иначе None.
        """
        currencies = {
            "manat": ["₼", "AZN"],
            "belarusian_ruble": ["Br", "BYR", "BYN"],
            "euro": ["€", "EUR"],
            "lari": ["₾", "GEL"],
            "som": ["с", "KGS"],
            "tenge": ["₸", "KZT"],
            "ruble": ["₽", "RUR", "RUB", "РУБ", "р.", "Рубль"],
            "grivna": ["₴", "UAH"],
            "dollar": ["$", "USD"],
            "uzbek_sum": ["Soʻm", "UZS"],
        }
        currency = currency.lower()
        for curr, symbols in currencies.items():
            for symbol in symbols:
                if symbol.lower() == currency:
                    return symbols[1]
        return None

    @staticmethod
    def get_sj_date_from() -> int:
        """
        Метод для получения начальной даты для SuperJob.

        Получает текущую дату с помощью метода `today` класса `date` модуля `datetime`,
        затем создает объект `datetime` с началом текущего дня с помощью метода
        `combine` класса `datetime`. Затем метод получает timestamp начала текущего дня
        с помощью метода `timestamp` и преобразует его в целое число.
        Полученное значение возвращается как результат работы метода.

        Returns:
            int: Начальная дата в формате timestamp.
        """
        today = datetime.date.today()
        start_time = datetime.datetime.combine(today, datetime.datetime.min.time())
        start_timestamp = start_time.timestamp()
        date_from = int(start_timestamp)
        return date_from

    @staticmethod
    def get_sj_date_to() -> int:
        """
        Метод для получения конечной даты для SuperJob.

        Метод создает объект `datetime` с текущим временем с помощью метода `now`
        класса `datetime` модуля `datetime`, затем получает timestamp текущего времени
        с помощью метода `timestamp` и преобразует его в целое число.
        Полученное значение возвращается как результат работы метода.

        Returns:
            int: Конечная дата в формате timestamp.
        """
        end_timestamp = datetime.datetime.now().timestamp()
        date_to = int(end_timestamp)
        return date_to

    @staticmethod
    def get_tv_date_from() -> str:
        """
        Метод для получения начальной даты для Trudvsem.

        Метод получает текущую дату, вычитает из нее 1 день с помощью метода `timedelta`
        класса `timedelta` модуля `datetime`, затем создает объект `datetime` с началом
        предыдущего дня с помощью метода `combine`. Затем метод преобразует объект
        `datetime` в строку в формате "YYYY-MM-DDTHH:MM:SSZ" с помощью метода
        `strftime`. Полученная строка возвращается как результат работы метода.

        Returns:
            str: Начальная дата в строковом формате.
        """
        today = datetime.date.today() - datetime.timedelta(days=1)
        today = datetime.datetime.combine(today, datetime.datetime.min.time())
        date_from = today.strftime("%Y-%m-%dT%H:%M:%SZ")
        return date_from

    @staticmethod
    def get_tv_date_to() -> str:
        """
        Метод для получения конечной даты для Trudvsem.

        Метод создает объект `datetime` с текущим временем с помощью метода `now`
        класса `datetime` модуля `datetime`, затем преобразует его в строку в формате
        "YYYY-MM-DDTHH:MM:SSZ" с помощью метода `strftime`.
        Полученная строка возвращается как результат работы метода.

        Returns:
            str: Конечная дата в строковом формате.
        """
        now = datetime.datetime.now()
        date_to = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        return date_to

    @staticmethod
    async def set_delay(delay: float) -> None:
        """
        Асинхронный метод для установки задержки между запросами.

        Метод устанавливает задержку между запросами на время, равное значению атрибута
        `delay`, с помощью функции `sleep` модуля `asyncio`.
        Args (delay: float): Задержка в секундах.
        Returns:
            None
        """
        await asyncio.sleep(delay)

    @staticmethod
    def get_data(request: HttpRequest) -> dict:
        """Метод получения данных из запроса.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            Any | None: Данные.
        """
        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            logger.exception(exc)
        return data

    @staticmethod
    def timeit(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            start = time.time()
            result = await f(*args, **kwargs)
            finish = time.time()
            logger.debug(f"Затрачено времени: {finish - start}")
            return result

        return wrapper
