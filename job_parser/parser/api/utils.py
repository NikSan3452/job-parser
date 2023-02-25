import datetime


class Utils:
    """Класс со вспомогательными методами"""

    @staticmethod
    def convert_date(date: str | datetime.date) -> float:
        """Проверяет формат даты и при необходимости конвертирует его.

        Args:
            date (str | datetime.date): Дата.

        Returns:
            float: Конвертированная дата.
        """
        if isinstance(date, datetime.date):
            converted_to_datetime = datetime.datetime.combine(date, datetime.time()).timestamp()
            return converted_to_datetime
        elif isinstance(date, str):
            converted_from_str = datetime.datetime.strptime(date, "%Y-%m-%d")
            converted_to_datetime = datetime.datetime.combine(
                converted_from_str, datetime.time()
            ).timestamp()
            return converted_to_datetime

    @staticmethod
    def check_date(date_from: str | None, date_to: str | None) -> tuple[datetime.date | str]:
        """Проверяет дату на пустое значение, если истина, то
        будет установлено значение по умолчанию.

        Args:
            date_from (str): Дата от.
            date_to (str): Дата до.

        Returns:
            datetime.date | str: Время задаваемое по умолчанию.
        """
        if date_from == "" or date_from is None:
            new_date_from = datetime.date.today() - datetime.timedelta(days=3)
        else:
            new_date_from = date_from

        if date_to == "" or date_to is None:
            new_date_to = datetime.date.today()
        else:
            new_date_to = date_to
        return new_date_from, new_date_to

    @staticmethod
    def sort_by_date(job_list: list[dict], key: str) -> list[dict]:
        """Сортирует список вакансий по дате.

        Args:
            job_list (list[dict]): Список вакансий.
            key (str): Ключь, по которому сортируем.

        Returns:
            list[dict]: Сортированный список вакансий.
        """
        sorted_list: list[dict] = sorted(job_list, key=lambda _dict: _dict[key], reverse=True)
        return sorted_list

    @staticmethod
    def sort_by_title(job_list: list[dict], title: str) -> list[dict]:
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
    def convert_experience(experience: int) -> str:
        """Конвертирует значения опыта работы в понятный
        для API HeadHunter и Zarplata вид.

        Args:
            experience (int): Опыт.

        Returns:
            str: Конвертированный опыт.
        """
        if experience == 1:
            experience = "noExperience"
        elif experience == 2:
            experience = "between1And3"
        elif experience == 3:
            experience = "between3And6"
        elif experience == 4:
            experience = "moreThan6"
        return experience

    @staticmethod
    def sorted_by_remote_work(remote: bool, job_list: list[dict]):
        sorted_list: list[dict] = []
        if remote:
            for job in job_list:
                if job.get("type_of_work") == "Удаленная работа":
                    sorted_list.append(job)
                elif job.get("place_of_work") == "Удалённая работа (на дому)":
                    sorted_list.append(job)
        return sorted_list

    @staticmethod
    def sorted_by_job_board(job_board: str, job_list: list[dict]) -> list[dict]:
        sorted_list: list[dict] = []
        for job in job_list:
            if job_board == job["job_board"]:
                sorted_list.append(job)
        return sorted_list
