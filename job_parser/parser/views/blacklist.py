import json

from django.db import DatabaseError, IntegrityError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

from parser.mixins import AsyncLoginRequiredMixin
from parser.models import Favourite, BlackList

# Логирование
setup_logging()


class AddToBlackListView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в черный список.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в черный список.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается создать или получить объект `BlackList`
        с указанными данными пользователя, URL и названием вакансии.
        Если все прошло успешно, в лог записывается информация об успешном добавлении
        вакансии в черный список. Также удаляется объект `Favourite`, если он
        существует.
        В случае возникновения исключения DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse 
        со статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешном добавлении
        вакансии в черный список.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном добавлении
            вакансии в черный список.
        """

        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        vacancy_url = data.get("url")
        vacancy_title = data.get("title")
        if not vacancy_url or not vacancy_title:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            await BlackList.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            await Favourite.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} добавлена в черный список")
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse(
            {"status": f"Вакансия {vacancy_url} добавлена в черный список"}
        )


class DeleteFromBlacklistView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из черного списка.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление вакансии из черного списка.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается удалить объект `BlackList`
        с указанными данными пользователя и URL вакансии.
        Если все прошло успешно, в лог записывается информация о том,
        что вакансия была удалена из черного списка.
        В случае возникновения исключений DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse 
        со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что вакансия была удалена из черного списка.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что вакансия была удалена из черного списка.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            data = json.load(request)
            vacancy_url = data.get("url")
            if not vacancy_url:
                return JsonResponse(
                    {"Ошибка": "Отсутствует обязательное поле 'url'"}, status=400
                )

            await BlackList.objects.filter(
                user=request.user, url=vacancy_url
            ).adelete()
            view_logger.info(f"Вакансия {vacancy_url} удалена из черного списка")
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse(
            {"status": f"Вакансия {vacancy_url} удалена из черного списка"}
        )


class ClearBlackList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки черного списка вакансий.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку черного списка вакансий.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Затем метод пытается удалить все объекты `BlackList` для
        конкретного пользователя.
        Если все прошло успешно, в лог записывается информация об успешной очистке
        черного списка.
        В случае возникновения исключения DatabaseError они
        записываются в лог и будет возвращен соответствующий JsonResponse со
        статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешной очистке
        черного списка.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке черного списка.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            await BlackList.objects.filter(user=request.user).adelete()
            view_logger.info("Черный список вакансий успешно очищен")
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Произошла ошибка базы данных"},
                status=500,
            )

        return JsonResponse({"status": "Черный список вакансий успешно очищен"})