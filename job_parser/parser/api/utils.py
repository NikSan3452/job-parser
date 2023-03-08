import datetime


class Utils:
    """Класс со вспомогательными методами"""

    @staticmethod
    async def convert_date(date: str | datetime.date) -> float:
        """Проверяет формат даты и при необходимости конвертирует его.

        Args:
            date (str | datetime.date): Дата.

        Returns:
            float: Конвертированная дата.
        """
        if isinstance(date, datetime.date):
            converted_to_datetime = datetime.datetime.combine(
                date, datetime.time()
            ).timestamp()
            return converted_to_datetime
        elif isinstance(date, str):
            converted_from_str = datetime.datetime.strptime(date, "%Y-%m-%d")
            converted_to_datetime = datetime.datetime.combine(
                converted_from_str, datetime.time()
            ).timestamp()
            return converted_to_datetime

    @staticmethod
    async def convert_date_for_trudvsem(date: datetime.date | str) -> str:
        """Проверяет формат даты и при необходимости конвертирует его.

        Args:
            date (datetime.date): Дата.

        Returns:
            str: Конвертированная дата.
        """
        if isinstance(date, datetime.date):
            datetime_obj = datetime.datetime.combine(date, datetime.time())
            converted_date = datetime_obj.strftime("%Y-%m-%dT%H:%M:%SZ")
        return converted_date

    @staticmethod
    async def check_date(
        date_from: str | None | datetime.date,
        date_to: str | None | datetime.date,
    ) -> tuple[datetime.date | str, datetime.date | str]:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str | None | datetime.date): Дата от.
            date_to (str | None | datetime.date): Дата до.

        Returns:
            tuple[datetime.date | str, datetime.date | str]: Время задаваемое по умолчанию.
        """
        if not date_from or date_from == "":
            new_date_from = datetime.date.today() - datetime.timedelta(days=3)
        elif isinstance(date_from, str):
            new_date_from = datetime.datetime.strptime(date_from, "%Y-%m-%d").date()
        else:
            new_date_from = date_from

        if not date_to or date_to == "":
            new_date_to = datetime.date.today()
        elif isinstance(date_to, str):
            new_date_to = datetime.datetime.strptime(date_to, "%Y-%m-%d").date()
        else:
            new_date_to = date_to
        return new_date_from, new_date_to

    @staticmethod
    async def sort_by_date(job_list: list[dict]) -> list[dict]:
        """Сортирует список вакансий по дате.

        Args:
            job_list (list[dict]): Список вакансий.
            key (str): Ключь, по которому сортируем.

        Returns:
            list[dict]: Сортированный список вакансий.
        """
        sorted_list: list[dict] = sorted(
            job_list, key=lambda _dict: _dict["published_at"], reverse=True
        )
        return sorted_list

    @staticmethod
    async def sort_by_title(job_list: list[dict], title: str) -> list[dict]:
        """Сортирует список вакансий по наличию в заголовке
        вакансии ключевого слова.

        Args:
            job_list (list[dict]): Список вакансий.
            title (str): Ключевое слово, по которому сортируем.

        Returns:
            list[dict]: Сортированный список вакансий.
        """
        sorted_list: list[dict] = []
        for job in job_list:
            if title in job["title"]:
                sorted_list.append(job)
        return sorted_list

    @staticmethod
    async def convert_experience(experience: int, scraper: bool = False) -> str:
        """Конвертирует значения опыта работы в понятный
        для API HeadHunter и Zarplata вид.

        Args:
            experience (int): Опыт.
            scraper (bool): Если True, будет конвертироваться опыт для скрапера.

        Returns:
            str: Конвертированный опыт.
        """
        if scraper:
            match experience:
                case 1:
                    converted_experience = "noExperience"
                case 2:
                    converted_experience = "between1And3"
                case 3:
                    converted_experience = "between3And6"
                case 4:
                    converted_experience = "moreThan6"
        else:
            match experience:
                case 1:
                    converted_experience = "Без опыта"
                case 2:
                    converted_experience = "от 1 до 3 лет"
                case 3:
                    converted_experience = "от 3 до 6 лет"
                case 4:
                    converted_experience = "от 6 лет"
        return converted_experience

    @staticmethod
    async def convert_experience_for_trudvsem(experience: int) -> tuple[int, int]:
        """Конвертирует значения опыта для API Trudvsem.

        Args:
            experience (int): Опыт из формы.

        Returns:
            tuple[int, int]: Кортеж из диапазона опыта в годах.
        """
        match experience:
            case 1:
                converted_experience = (0, 1)
            case 2:
                converted_experience = (1, 3)
            case 3:
                converted_experience = (3, 6)
            case 4:
                converted_experience = (6, 10)
        return converted_experience

    @staticmethod
    async def sort_by_remote_work(remote: bool, job_list: list[dict]):
        """Сортирует вакансии по удаленной работе.

        Args:
            remote (bool): Если истина, то работа считается удаленной.
            job_list (list[dict]): Список вакансий.

        Returns:
            _type_: Сортированный список вакансий.
        """
        sorted_list: list[dict] = []
        if remote:
            for job in job_list:
                if job.get("type_of_work") == "Удаленная работа":
                    sorted_list.append(job)
                elif job.get("place_of_work") == "Удалённая работа (на дому)":
                    sorted_list.append(job)
                elif "удаленная" in job.get("responsibility", "").lower():
                    sorted_list.append(job)
                elif "удаленная" in job.get("title", "").lower():
                    sorted_list.append(job)
        return sorted_list