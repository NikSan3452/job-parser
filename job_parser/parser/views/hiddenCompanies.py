import json

from django.db import DatabaseError, IntegrityError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

from parser.mixins import AsyncLoginRequiredMixin
from parser.models import HiddenCompanies
from parser.parsing.utils import Utils

# Логирование
setup_logging()

utils = Utils()


class HideCompanyView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для сокрытия вакансий выбранных компаний.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на скрытие компании.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается создать или получить объект `HiddenCompanies`
        с указанными данными пользователя и названием компании.
        Если все прошло успешно, в лог записывается информация о том,
        что компания была скрыта.
        В случае возникновения исключения DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со 
        статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что компания была скрыта.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была скрыта.
        """
        view_logger = logger.bind(request=request.POST)

        try:
            data = json.load(request)
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        company = data.get("company")
        if not company:
            return JsonResponse({"Ошибка": "Отсутствуют обязательные поля"}, status=400)

        try:
            await HiddenCompanies.objects.aget_or_create(
                user=request.user, name=company
            )
            view_logger.info(f"Компания {company} скрыта")
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": f"Компания {company} скрыта"})


class DeleteFromHiddenCompaniesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления компании из списка скрытых.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление компании из списка скрытых.

        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.
        Внутри метода создается логгер с привязкой к данным запроса.
        Данные из запроса десериализуются в блоке try/except и в случае успеха
        загружаются в переменную `data`, из которой извлекается URL вакансии.
        В противном случае будет вызвано исключение JSONDecodeError с последующей
        отправкой соответствующего ответа JsonResponse со статусом 400.
        Если URL вакансии отсутствует, будет возвращен соответствующий JsonResponse
        со статусом 400.
        Затем метод пытается удалить объект `HiddenCompanies`
        с указанными данными пользователя и названием компании.
        Если все прошло успешно, в лог записывается информация о том,
        что компания была удалена из списка скрытых.
        В случае возникновения исключений DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse
        со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что компания была удалена из списка скрытых.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была удалена из списка скрытых.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            data = json.load(request)
            company = data.get("name")
            if not company:
                return JsonResponse(
                    {"Ошибка": "Отсутствует обязательное поле 'name'"}, status=400
                )

            await HiddenCompanies.objects.filter(
                user=request.user, name=company
            ).adelete()
            view_logger.info(f"Компания {company} удалена из списка скрытых")
        except json.JSONDecodeError as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        except (DatabaseError, IntegrityError) as exc:
            view_logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": f"Компания {company} удалена из списка скрытых"})


class ClearHiddenCompaniesList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки списка скрытых компаний.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку списка скрытых компаний.
        Этот метод принимает объект запроса `request` и обрабатывает его асинхронно.

        Внутри метода создается логгер с привязкой к данным запроса.
        Затем метод пытается удалить все объекты `HiddenCompanies` для
        конкретного пользователя.
        Если все прошло успешно, в лог записывается информация об успешной очистке
        списка скрытых компаний.
        В случае возникновения исключения DatabaseError они
        записываются в лог и будет возвращен соответствующий JsonResponse со
        статусом 500.
        В конце метода возвращается JSON-ответ с информацией об успешной очистке
        списка скрытых компаний.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке списка скрытых компаний.
        """
        view_logger = logger.bind(request=request.POST)
        try:
            await HiddenCompanies.objects.filter(user=request.user).adelete()
            view_logger.info("Список скрытых компаний успешно очищен")
        except DatabaseError as exc:
            view_logger.exception(exc)
            return JsonResponse(
                {"Ошибка": "Произошла ошибка базы данных"},
                status=500,
            )

        return JsonResponse({"status": "Список скрытых компаний успешно очищен"})
