from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

from parser.mixins import AsyncLoginRequiredMixin
from parser.models import UserVacancies
from parser.utils import Utils

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

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была скрыта.
        """
        data = Utils.get_data(request)
        company = data.get("company", None)
        if not company:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.hide_company(request, company)
        return JsonResponse({"status": f"Компания {company} скрыта"})

    async def hide_company(self, request: HttpRequest, company: str) -> None:
        try:
            vacancy, created = await UserVacancies.objects.aget_or_create(
                user=request.user, hidden_company=company
            )
            vacancy.is_favourite = False
            vacancy.is_blacklist = False
            vacancy.save()
            logger.info(f"Компания {company} скрыта")
        except Exception as exc:
            logger.exception(exc)


class DeleteFromHiddenCompaniesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления компании из списка скрытых.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """
        Метод обработки POST-запроса на удаление компании из списка скрытых.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией о том,
            что компания была удалена из списка скрытых.
        """
        data = Utils.get_data(request)
        company = data.get("name")
        if not company:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.delete_from_hidden(request, company)
        return JsonResponse({"status": f"Компания {company} удалена из списка скрытых"})

    async def delete_from_hidden(self, request: HttpRequest, company: str) -> None:
        try:
            vacancy = await UserVacancies.objects.filter(
                user=request.user, hidden_company=company
            ).afirst()
            if not vacancy:
                pass
            elif not vacancy.is_blacklist and not vacancy.is_favourite:
                vacancy.delete()
            else:
                vacancy.hidden_company = None
                vacancy.save()
            logger.info(f"Компания {company} удалена из списка скрытых")
        except Exception as exc:
            logger.exception(exc)


class ClearHiddenCompaniesList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки списка скрытых компаний.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку списка скрытых компаний.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке списка скрытых компаний.
        """
        try:
            vacancies = UserVacancies.objects.filter(user=request.user)
            for vacancy in vacancies:
                if not vacancy.is_blacklist and not vacancy.is_favourite:
                    vacancy.delete()
                else:
                    vacancy.hidden_company = None
                    vacancy.save()

            logger.info("Список скрытых компаний успешно очищен")
        except DatabaseError as exc:
            logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": "Список скрытых компаний успешно очищен"})
