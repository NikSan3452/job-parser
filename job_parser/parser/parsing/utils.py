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
                    converted_experience = "от 1 до 3 лет"
                case 3:
                    converted_experience = "от 3 до 6 лет"
                case 4:
                    converted_experience = "от 6 лет"
        elif job_board == "Trudvsem":
            match experience:
                case 0:
                    converted_experience = "Нет опыта"
                case 1 | 2 | 3:
                    converted_experience = "от 1 до 3 лет"
                case 4 | 5 | 6:
                    converted_experience = "от 3 до 6 лет"
                case _ if experience > 6:
                    converted_experience = "от 6 лет"
                    
        return converted_experience