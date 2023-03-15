import httpx
import json
from typing import Optional

from logger import setup_logging, logger

# Логирование
setup_logging()


class CreateConnection:
    """Класс подключения к API площадок"""

    @logger.catch(message="Ошибка в методе CreateConnection.create_session()")
    async def create_session(
        self,
        url: str,
        headers: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> str:
        """Отвечает за создание запросов к API.

        Args:
            url (str): URL - адрес API.
            headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.
            params (Optional[dict], optional): Параметры запроса. По умолчанию None.

        Returns:
            str: Контент в виде строки.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
            data = response.content.decode()
        return data


class Parser:
    """Основной класс парсера."""

    general_job_list: list[dict] = []
    connection = CreateConnection()

    async def get_vacancies(
        self,
        url: str,
        params: dict,
        pages: int,
        headers: Optional[dict] = None,
        items: Optional[str] = None,
    ) -> list[dict]:
        """Отвечает за постраничное получение вакансий.

        Args:
            url (str): URL - адрес API.
            params (dict): Параметры запроса.
            page_range (int): Диапазон страниц (максимум 20)
            с общим количеством страниц, которые вернул сервер. Т.к у каждого API
            разное название этого параметра, его нужно передать здесь.
            Необходимо для проверки на последнюю страницу.
            headers (Optional[dict]): Заголовки запроса. По умолчанию None.
            items: Optional[str]: Ключ в возвращаемом API словаре, по которому
            мы можем получить доступ к списку вкансий.
        Returns:
            list[dict]: Список вакансий или исключение.
        """
        job_list: list[dict] = []
        data: str = ""
        json_data: dict = {}

        for page in range(pages):  # Постраничный вывод вакансий
            try:
                # Получаем данные
                data = await self.connection.create_session(url, headers, params)
                json_data = json.loads(data)  # Упаковываем в json
            except Exception as exc:
                logger.exception(exc)

            if items == "results":  # Если запрос к сайту Trudvsem
                vacancies: dict = {}
                if json_data.get(items):
                    # На каждой итерации получаем новый список вакансий
                    vacancies = json_data[items]["vacancies"]
                    if vacancies:  # Если в списке есть данные-добавим их в общий список
                        job_list.extend(vacancies)
                    if vacancies is None:  # Если список пуст, запросы останавливаются
                        break
            else:  # Если запрос к другим сайтам получим список вакансий и
                job_list.extend(json_data.get(items, ""))  # добавим их в общий список
                # Если список пуст запросы останавливаются
                if len(json_data.get(items, "")) == 0:
                    break

            page += 1

            # Устанавливаем смещение
            if items == "results":
                params["offset"] = page
            else:
                params["page"] = page
                
        return job_list
