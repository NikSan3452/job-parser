import httpx
import orjson
from typing import Optional
from logger import setup_logging, logger

# Логирование
setup_logging()


class Parser:
    """Основной класс парсера."""

    general_job_list: list[dict] = []

    @logger.catch(message="Ошибка в методе Parser.create_session()")
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

    async def get_vacancies(
        self,
        url: str,
        params: dict,
        pages: int,
        total_pages: str,
        headers: Optional[dict] = None,
    ) -> list[dict] | str:
        """Отвечает за постраничное получение вакансий.

        Args:
            url (str): URL - адрес API.
            params (dict): Параметры запроса.
            page_range (int): Диапазон страниц (максимум 20)
            total_pages (str): Строковое представление ключа словаря
            с общим количеством страниц, которые вернул сервер. Т.к у каждого API
            разное название этого параметра, его нужно передать здесь.
            Необходимо для проверки на последнюю страницу.
            headers (Optional[dict], optional): Заголовки запроса. По умолчанию None.

        Returns:
            list[dict] | str: Список вакансий или исключение.
        """
        job_list: list[dict] = []
        for page in range(pages):  # Постраничный вывод вакансий
            params["page"] = page
            page += 1
            try:
                data = await self.create_session(
                    url=url, params=params, headers=headers
                )
                json_data = orjson.loads(data)
                job_list.append(json_data)

                if (
                    job_list[0][total_pages] - page
                ) <= 1:  # Проверка на последнюю страницу
                    break
            except httpx.RequestError as exc:
                logger.exception(exc)

        return job_list
