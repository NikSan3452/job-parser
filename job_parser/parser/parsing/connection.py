from parser.parsing.config import ParserConfig

import httpx

config = ParserConfig()


class Session:
    """Класс для создания запросов к API.

    Данный класс содержит в себе асинхронный метод для создания клиента и отправки
    запросов на указанный URL
    """

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
        headers.update(config.update_headers(url))

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url=url, headers=headers, params=params, timeout=10
            )
        return response
