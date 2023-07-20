import json
from parser.parsing.connection import WebClient

from loguru import logger


class Fetcher:
    """
    Класс для выборки вакансий из полученных от API данных.
    """
    def __init__(
        self,
        job_board: str,
        url: str,
        params: dict,
        pages: int,
        items: str,
        client: WebClient,
    ) -> None:
        self.job_board = job_board
        self.url = url
        self.params = params
        self.pages = pages
        self.items = items
        self.client = client

    async def get_vacancies(self) -> list[dict]:
        """
        Асинхронный метод для получения списка вакансий.

        Метод возвращает список словарей с данными о вакансиях. Метод проходит по всем
        страницам с вакансиями (количество страниц задается атрибутом `pages`), получает
        данные о вакансиях с помощью метода `get_data`, обрабатывает полученные данные
        с помощью метода `process_data` и добавляет их в список вакансий.
        Если обработанные данные равны `None`, то цикл прерывается. В конце каждой
        итерации цикла значение параметра `offset` или `page`
        (в зависимости от значения атрибута `items`) увеличивается на 1.
        В конце работы метода возвращается список вакансий.

        Returns:
            vacancy_list(list[dict]): Список словарей с данными о вакансиях.
        """
        vacancy_list: list[dict] = []

        for page in range(self.pages):
            json_data = await self.get_data(self.url)
            vacancies = await self.process_data(json_data)
            if vacancies is None:
                break
            else:
                vacancy_list.extend(vacancies)
            page += 1
            self.params["offset" if self.items == "results" else "page"] = page
        return vacancy_list

    async def get_data(self, url: str) -> dict:
        """
        Асинхронный метод для получения данных с указанного URL.

        Метод принимает на вход URL-адрес и возвращает словарь с данными.
        Создает соединение с помощью метода `create_client` объекта `session`, передавая
        ему URL-адрес и параметры запроса (атрибут `params`). Затем метод получает
        содержимое ответа, декодирует его и преобразует в словарь с помощью модуля
        `json`. Полученный словарь возвращается как результат работы метода. Если во
        время работы метода возникает исключение, то оно логируется с помощью метода
        `exception` объекта `logger`, а метод возвращает пустой словарь.

        Args:
            url (str): URL для получения данных.

        Returns:
            dict: Словарь с данными.
        """
        try:
            response = await self.client.create_client(url, self.params)
            data = response.content.decode()
            json_data = json.loads(data)
            return json_data
        except Exception as exc:
            logger.exception(exc)
            return {}

    async def process_data(self, json_data: dict) -> list[dict] | None:
        """
        Асинхронный метод для обработки данных, полученных с указанного URL.

        Метод проверяет значение параметра items. Если items равен None, вернется None.
        Если items равен 'results', то попытается получить вакансии по ключу
        'vacancies'.
        Иначе вернет данные по ключу 'items'.
        Args:
            json_data (dict): Словарь с данными для обработки.
            items (str | None): Ключ для получения данных из словаря json_data.

        Returns:
            list[dict] | None: Список словарей с информацией о вакансиях или None,
            если данные отсутствуют.
        """
        data = json_data.get(self.items, None)
        if data is None or len(data) == 0:
            return None
        elif self.items == "results":
            return json_data[self.items]["vacancies"]
        else:
            return data

    async def get_vacancy_details(self, vacancy: dict) -> dict | None:
        """
        Асинхронный метод для получения деталей вакансии.

        Метод принимает на вход словарь с данными о вакансии и возвращает словарь
        с деталями конкретной вакансии. Метод получает идентификатор вакансии из словаря
        с данными с помощью метода `get_data`. Полученные данные возвращаются,
        как результат работы метода.

        Args:
            vacancy (dict): Словарь с данными о вакансии.

        Returns:
            details (dict): Словарь с деталями вакансии.
        """
        details = None
        vacancy_id = vacancy.get("id", None)
        if vacancy_id:
            details = await self.get_data(f"{self.url}/{vacancy_id}")
        return details
