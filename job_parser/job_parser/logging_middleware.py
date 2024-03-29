import time
import uuid
from typing import Any

from django.http import HttpRequest
from loguru import logger


def logging_middleware(get_response) -> Any:
    """Промежуточное ПО для регистрации информации о запросе и ответе.

    Это промежуточное ПО регистрирует информацию о входящих запросах и исходящих 
    ответах, включая путь запроса, метод, статус код ответа, размер ответа и время 
    выполнения запроса.
    Также добавляет идентификатор запроса в заголовок ответа "X-Request-ID".

    Args:
        get_response: Функция для получения ответа на запрос.

    Returns:
        Функция middleware (Any), которая принимает запрос и возвращает ответ.
    """

    def middleware(request: HttpRequest) -> Any:
        # Создаем идентификатор запроса
        request_id = str(uuid.uuid4())

        # Добавляем контекст ко всем регистраторам во всех представлениях
        with logger.contextualize(request_id=request_id):
            request.start_time = time.time()

            response = get_response(request)

            elapsed = time.time() - request.start_time

            # После получения ответа
            logger.bind(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                response_size=len(response.content),
                elapsed=elapsed,
            ).info(
                "Входящий метод '{method}' запросил адрес '{path}'",
                method=request.method,
                path=request.path,
            )

            response["X-Request-ID"] = request_id

            return response

    return middleware
