import datetime


class Utils:
    @staticmethod
    def check_date_from(
        date_from: str | None | datetime.date,
    ) -> datetime.date | str:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str | None | datetime.date): Дата от.

        Returns:
            datetime.date | str: Время задаваемое по
            умолчанию.
        """
        if not date_from or date_from == "":
            new_date_from = datetime.date.today() - datetime.timedelta(days=1)
        elif isinstance(date_from, str):
            new_date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
        else:
            new_date_from = date_from
        return new_date_from

    @staticmethod
    def check_date_to(
        date_to: str | None | datetime.date,
    ) -> datetime.date | str:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_to (str | None | datetime.date): Дата до.

        Returns:
            datetime.date | str: Время задаваемое по
            умолчанию.
        """
        if not date_to or date_to == "":
            new_date_to = datetime.date.today()
        elif isinstance(date_to, str):
            new_date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            new_date_to = date_to
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