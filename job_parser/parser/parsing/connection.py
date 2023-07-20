from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from parser.parsing.config import ParserConfig


class WebClient:
    """Класс для создания запросов к API.

    Данный класс содержит в себе асинхронный метод для создания клиента и отправки
    запросов на указанный URL
    """

    def __init__(self, config: "ParserConfig") -> None:
        self.config = config

    async def create_client(
        self,
        url: str,
        params: dict | None = None,
    ) -> httpx.Response:
        """
        Асинхронный метод для создания клиента и отправки запросов на указанный URL.

        Метод в начале создает пустой словарь headers для хранения заголовков запроса.
        Затем с каждым запросом обновляет словарь новыми заголовками.
        Далее создает асинхронный клиент httpx.AsyncClient и отправляет запрос на
        указанный URL с указанными заголовками и параметрами.
        Возвращает ответ сервера на запрос.

        Args:
            url (str): URL-адрес для отправки GET-запроса.
            params (dict | None, optional): Параметры запроса. По умолчанию None.

        Returns:
            httpx.Response: Ответ сервера на запрос.
        """
        headers: dict = {}
        headers.update(self.config.update_headers(url))

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url, headers=headers, params=params, timeout=10
            )
        return response
