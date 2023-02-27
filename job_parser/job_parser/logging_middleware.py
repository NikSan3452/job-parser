from loguru import logger
import uuid
import time


def logging_middleware(get_response):
    def middleware(request):
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
