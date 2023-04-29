import abc
import json
import random
from parser.api.config import ParserConfig

import httpx
from logger import logger, setup_logging

# Логирование
setup_logging()

config = ParserConfig()


class CreateConnection:
    """Класс для создания запросов к API.

    Данный класс содержит в себе асинхронный метод для создания клиента и отправки
    GET-запросов на указанный URL
    """

    async def create_client(
        self,
        url: str,
        params: dict | None = None,
    ) -> httpx.Response:
        """
        Асинхронный метод для создания клиента и отправки GET-запросов на указанный URL.

        Метод в начале создает пустой словарь headers для хранения заголовков запроса.
        Если URL-адрес принадлежит api superjob, то добавляет в headers ключ приложения
        "x-api-app-id" со случайным значением из списка конфигурации
        config.superjob_secret_keys_list.
        Далее создает асинхронный клиент httpx.AsyncClient и отправляет GET-запрос на
        указанный URL с указанными заголовками и параметрами.
        Возвращает ответ сервера на запрос.

        Args:
            url (str): URL-адрес для отправки GET-запроса.
            params (dict | None, optional): Параметры запроса. По умолчанию None.

        Returns:
            httpx.Response: Ответ сервера на запрос.
        """
        headers = {}
        if url == config.superjob_url:
            headers["x-api-app-id"] = random.choice(config.superjob_secret_keys_list)

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers, params=params)
        return response


class Parser(abc.ABC):
    """
    Базовый класс парсера вакансий.

    Наследуется от абстрактного базового класса abc.ABC.

    Класс Parser предназначен для парсинга вакансий с различных сайтов.
    Он содержит абстрактные методы для получения информации о вакансиях, такие как
    URL-адрес, название, зарплата, город и другие. Эти методы должны быть реализованы в
    дочерних классах для каждого сайта индивидуально.

    Attributes:
        general_job_list (list[dict]): Общий (главный) список с вакансиями.
        connection (CreateConnection): Экземпляр класса CreateConnection для создания
        соединения с API.
    """

    general_job_list: list[dict] = []
    connection = CreateConnection()

    async def get_vacancies(
        self,
        url: str,
        params: dict,
        pages: int,
        items: str | None = None,
    ) -> list[dict]:
        """
        Асинхронный метод для получения списка вакансий с указанного URL.

        Метод проходит по указанному диапазону страниц и получает данные с помощью
        метода get_data.
        Если параметр items передается из парсера Trudvsem и равен "results",
        то обрабатывает данные с помощью метода process_trudvsem_data.
        Если список вакансий пуст, то останавливает запросы к API.
        Иначе добавляет их в общий список вакансий job_list.
        Далее увеличивает номер страницы и обновляет параметры запроса.

        Args:
            url (str): URL-адрес для отправки GET-запроса.
            params (dict): Параметры запроса.
            pages (int): Количество страниц для обработки.
            items (str | None, optional): Ключ для получения вакансий из json_data.
            По умолчанию None.

        Returns:
            list[dict]: Список словарей с информацией о вакансиях.
        """
        job_list: list[dict] = []

        for page in range(pages):
            json_data = await self.get_data(url, params)
            if items == "results":
                vacancies = await self.process_trudvsem_data(json_data, items)
                if vacancies is None:
                    break
                else:
                    job_list.extend(vacancies)
            else:
                vacancies = json_data.get(items, None)
                if not vacancies or len(vacancies) == 0:
                    break
                else:
                    job_list.extend(vacancies)
            page += 1
            if items == "results":
                params["offset"] = page
            else:
                params["page"] = page

        return job_list

    async def get_data(self, url: str, params: dict) -> dict:
        """
        Асинхронный метод для получения данных с указанного URL.

        Метод создает соединение с сервером с помощью метода create_client
        класса CreateConnection.
        Получает ответ сервера и декодирует его содержимое.
        Преобразует данные в формате JSON в словарь и возвращает его.
        В случае ошибки логирует ее и возвращает пустой словарь.

        Args:
            url (str): URL-адрес для отправки GET-запроса.
            params (dict): Параметры запроса.

        Returns:
            dict: Словарь с данными, полученными от сервера.
        """
        try:
            response = await self.connection.create_client(url, params)
            data = response.content.decode()
            json_data = json.loads(data)
            return json_data
        except (json.JSONDecodeError, AttributeError) as exc:
            logger.exception(exc)
            return {}

    async def process_trudvsem_data(
        self, json_data: dict, items: str
    ) -> list[dict] | None:
        """
        Асинхронный метод для обработки данных от API Trudvsem.

        Метод проверяет наличие ключа items в json_data и наличие вакансий
        по этому ключу.
        Если вакансии есть, то возвращает их. Иначе возвращает None.

        Args:
            json_data (dict): Словарь с данными от сервера.
            items (str): Ключ для получения вакансий из json_data.

        Returns:
            list[dict] | None: Список словарей с информацией о вакансиях или None,
            если вакансий нет.
        """
        if json_data.get(items) is None or len(json_data.get(items)) == 0:
            return None
        else:
            vacancies = json_data[items]["vacancies"]
            return vacancies

    async def vacancy_parsing(
        self, url: str, params: dict, job_board: str, pages: int, items: str
    ) -> dict:
        """
        Асинхронный метод для парсинга вакансий с указанного URL.

        Метод получает список вакансий с помощью метода get_vacancies и формирует
        словарь с информацией о каждой вакансии.
        Если площадка "Trudvsem", то проверяет наличие города в параметрах запроса и
        наличие этого города в информации о вакансии.
        Если город есть, то добавляет словарь с информацией о вакансии в общий список
        всех вакансий.
        Иначе добавляет словарь с информацией о вакансии в общий список всех вакансий
        без проверки города.

        Args:
            url (str): URL-адрес для отправки GET-запроса.
            params (dict): Параметры запроса.
            job_board (str): Название сайта для парсинга вакансий.
            pages (int): Количество страниц для обработки.
            items (str): Ключ для получения вакансий из json_data.

        Returns:
            dict: Словарь с информацией о последней обработанной вакансии.
        """
        job_list = await self.get_vacancies(
            url=url,
            params=params,
            pages=pages,
            items=items,
        )

        # Формируем словарь с вакансиями
        job_dict: dict = {}
        for job in job_list:
            job_dict = {
                "job_board": job_board,
                "url": await self.get_url(job),
                "title": await self.get_title(job),
                "salary_from": await self.get_salary_from(job),
                "salary_to": await self.get_salary_to(job),
                "salary_currency": await self.get_salary_currency(job),
                "responsibility": await self.get_responsibility(job),
                "requirement": await self.get_requirement(job),
                "city": await self.get_city(job),
                "company": await self.get_company(job),
                "type_of_work": await self.get_type_of_work(job),
                "published_at": await self.get_published_at(job),
            }
            # В API площадки Trudvsem на момент написания кода Trudvsem отсутствует
            # поиск по городам поэтому реализуем его сами
            if job_board == "Trudvsem":
                city = params.get("city", None)
                if city is not None:
                    job_city = job_dict.get("city", "")
                    if job_city is not None and city.lower() in job_city.lower():
                        Parser.general_job_list.append(job_dict.copy())
                    else:
                        Parser.general_job_list.append(job_dict.copy())

            # Добавляем словарь с вакансией в общий список вакансий
            Parser.general_job_list.append(job_dict.copy())

        logger.debug(f"Сбор вакансий с {job_board} завершен")

        return job_dict

    @abc.abstractmethod
    async def get_request_params(self) -> dict:
        """
        Абстрактный асинхронный метод для получения параметров запроса.

        Returns:
            dict: Словарь с параметрами запроса.
        """
        pass

    @abc.abstractmethod
    async def get_url(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения URL-адреса вакансии.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: URL-адрес вакансии или None, если URL-адрес отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_title(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения названия вакансии.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название вакансии или None, если название отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_from(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения минимальной зарплаты.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Минимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_to(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения максимальной зарплаты.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Максимальная зарплата по вакансии или None, если зарплата
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_salary_currency(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения валюты зарплаты.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Валюта зарплаты по вакансии или None, если зарплата отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_responsibility(self, job: dict) -> str:
        """
        Абстрактный асинхронный метод для получения информации об обязанностях.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str: Информация об обязанностях по вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_requirement(self, job: dict) -> str:
        """
        Абстрактный асинхронный метод для получения информации о требованиях к
        кандидату.

        Args:
            job (dict): Словарь с информацией о вакансии.
        Returns:
            str: Информация о требованиях к кандидату по вакансии.
        """
        pass

    @abc.abstractmethod
    async def get_city(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения города.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Город вакансии или None, если город отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_company(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения названия компании.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Название компании по вакансии или None, если название
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_type_of_work(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения типа занятости.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Тип занятости по вакансии или None, если тип занятости
            отсутствует.
        """
        pass

    @abc.abstractmethod
    async def get_published_at(self, job: dict) -> str | None:
        """
        Абстрактный асинхронный метод для получения даты публикации вакансии.

        Args:
            job (dict): Словарь с информацией о вакансии.

        Returns:
            str | None: Дата публикации вакансии или None, если дата отсутствует.
        """
        pass
