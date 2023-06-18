import json

from django.db import DatabaseError, IntegrityError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

from parser.mixins import AsyncLoginRequiredMixin
from parser.models import Favourite

# Логирование
setup_logging()


class AddToFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в избранное.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в избранное.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса  десериализуются в блоке try/except и случае успеха
        загружаются в переменную `data`, из которой извлекается URL
        и название вакансии. В противном случае будет вызвано исключение JSONDecodeError
        с последующей отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL и название вакансии вакансии отсутствуют будет возвращен
        соответствующий JsonResponse со статусом 400.
        Затем метод пытается создать или получить объект `Favourite`
        с указанными данными пользователя, URL и названием вакансии.
        Если все прошло успешно, в лог записывается информация об успешном добавлении
        вакансии в избранное.
        В случае возникновения исключения IntegrityError или DatabaseError они 
        записываются в лог и будет возвращен соответствующий JsonResponse 
        со статусом 400 или 500.
        В конце метода возвращается JSON-ответ с информацией об успешном добавлении
        вакансии в избранное.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешном добавлении вакансии в избранное.
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
            await Favourite.objects.aget_or_create(
                user=request.user, url=vacancy_url, title=vacancy_title
            )
            view_logger.info(f"Вакансия {vacancy_title} добавлена в избранное")
        except IntegrityError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Такая вакансия уже есть в избранном"}, status=400
            )
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Произошла ошибка базы данных"},
                status=500,
            )

        return JsonResponse(
            {"status": f"Вакансия {vacancy_title} добавлена в избранное"}
        )


class DeleteFromFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из списка избранных.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на удаление вакансии из избранного.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается получить объект `Favourite` с указанными данными
        пользователя и URL вакансии. Если объект существует, он удаляется, и в лог
        записывается информация об успешном удалении вакансии из избранного.
        В случае возникновения исключения DatabaseError оно записывается в лог и
        будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешном удалении
        вакансии из избранного.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном удалении
            вакансии из избранного.
        """
        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        vacancy_url = data.get("url")
        if not vacancy_url:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            obj = await Favourite.objects.filter(
                user=request.user, url=vacancy_url
            ).afirst()
            if not obj:
                return JsonResponse(
                    {"Ошибка": f"Вакансия {vacancy_url} не найдена"}, status=404
                )
            else:
                obj.delete()
                view_logger.info(f"Вакансия {vacancy_url} удалена из избранного")
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)
        return JsonResponse({"status": f"Вакансия {vacancy_url} удалена из избранного"})


class ClearFavouriteList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки списка избранных вакансий.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку списка избранных вакансий.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Затем метод пытается удалить все объекты `Favourite` для
        конкретного пользователя.
        Если все прошло успешно, в лог записывается информация об успешной очистке
        списка избранного.
        В случае возникновения исключения DatabaseError они
        записываются в лог и будет возвращен соответствующий JsonResponse со
        статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешной очистке
        списка избранного.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке списка избранного.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            await Favourite.objects.filter(user=request.user).adelete()
            view_logger.info("Список избранных вакансий успешно очищен")
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Произошла ошибка базы данных"},
                status=500,
            )

        return JsonResponse({"status": "Список избранных вакансий успешно очищен"})
