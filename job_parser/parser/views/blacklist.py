from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

from parser.mixins import AsyncLoginRequiredMixin
from parser.models import UserVacancies, Vacancies
from parser.utils import Utils

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

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном добавлении вакансии
            в черный список.
        """
        data = Utils.get_data(request)
        pk = data.get("pk", None)
        if not pk:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.add_to_blacklist(request, pk)
        return JsonResponse({"status": f"Вакансия {pk} добавлена в черный список"})

    async def add_to_blacklist(self, request: HttpRequest, pk: str) -> None:
        """Асинхронный метод добавления вакансии в черный список.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.
            title (str): Название вакансии.

        Returns:
            None
        """
        try:
            vacancy = await Vacancies.objects.aget(pk=pk)
            user_vacancy, created = await UserVacancies.objects.aget_or_create(
                user=request.user, vacancy=vacancy
            )
            user_vacancy.is_blacklist = True
            user_vacancy.save()

            user_vacancy.is_favourite = False
            user_vacancy.save()

            logger.info(f"Вакансия {pk} добавлена в черный список")
        except Exception as exc:
            logger.exception(exc)


class DeleteFromBlacklistView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из черного списка.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на удаление вакансии из черного списка.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном удалении вакансии
            из черного списка.
        """
        data = Utils.get_data(request)
        pk = data.get("pk", None)
        if not pk:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.delete_from_blacklist(request, pk)
        return JsonResponse({"status": f"Вакансия {pk} удалена из черного списка"})

    async def delete_from_blacklist(self, request: HttpRequest, pk: str) -> None:
        """Асинхронный метод удаления вакансии из черного списка.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.

        Returns:
            None
        """
        try:
            vacancy = await Vacancies.objects.aget(pk=pk)
            user_vacancy = await UserVacancies.objects.filter(
                user=request.user, vacancy=vacancy
            ).afirst()
            if not user_vacancy:
                pass
            elif (
                user_vacancy.is_blacklist
                and not user_vacancy.is_favourite
                and not user_vacancy.hidden_company
            ):
                user_vacancy.delete()
            else:
                user_vacancy.is_blacklist = True
                user_vacancy.save()

            logger.info(f"Вакансия {pk} удалена из черного списка")

        except Exception as exc:
            logger.exception(exc)


class ClearBlackList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки черного списка вакансий.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку черного списка вакансий.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке черного списка.
        """
        try:
            vacancies = UserVacancies.objects.filter(user=request.user)
            for vacancy in vacancies:
                if (
                    vacancy.is_blacklist
                    and not vacancy.is_favourite
                    and not vacancy.hidden_company
                ):
                    vacancy.delete()
                else:
                    vacancy.is_blacklist = True
                    vacancy.save()
            logger.info("Черный список вакансий успешно очищен")
        except DatabaseError as exc:
            logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": "Черный список вакансий успешно очищен"})
