import json
import time

import httpx
from logger import logger, setup_logging

# Логирование
setup_logging()


class CreateConnection:
    """Класс подключения к API площадок"""

    @logger.catch(message="Ошибка в методе CreateConnection.create_session()")
    async def create_session(
        self,
        url: str,
        headers: dict | None = None,
        params: dict | None = None,
    ) -> httpx.Response:
        """Отвечает за создание запросов к API.

        Args:
            url (str): URL - адрес API.
            headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.
            params (Optional[dict], optional): Параметры запроса. По умолчанию None.

        Returns:
            httpx.Response: Тело ответа.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
        return response


class Parser:
    """Основной класс парсера."""

    general_job_list: list[dict] = []
    connection = CreateConnection()

    async def get_vacancies(
        self,
        url: str,
        params: dict,
        pages: int,
        headers: dict | None = None,
        items: str | None = None,
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

        start = time.time()

        for page in range(pages):  # Постраничный вывод вакансий
            try:
                # Получаем данные
                response = await self.connection.create_session(url, headers, params)
                data = response.content.decode()
                json_data = json.loads(data)  # Упаковываем в json
            except Exception as exc:
                logger.exception(exc)

            if items == "results":  # Если запрос к сайту Trudvsem
                vacancies: dict = {}
                # Если данные отсуствуют то запросы прерываются
                if json_data.get(items) is None or len(json_data.get(items)) == 0:
                    break
                else:
                    # На каждой итерации получаем новый список вакансий
                    vacancies = json_data[items]["vacancies"]
                    if vacancies:  # Если в списке есть данные-добавим их в общий список
                        job_list.extend(vacancies)
            else:  # Если запрос к другим сайтам получим список вакансий и
                job_list.extend(json_data.get(items, None))  # добавим их в общий список
                # Если список пуст запросы останавливаются
                if len(json_data.get(items, None)) == 0:
                    break

            page += 1

            # Устанавливаем смещение
            if items == "results":
                params["offset"] = page
            else:
                params["page"] = page

        end = time.time() - start

        logger.debug(f"Время затраченное на сбор: {round(end, 2)}")
        return job_list
