from parser.mixins import AsyncLoginRequiredMixin
from parser.models import UserVacancies
from parser.utils import Utils

from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

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
        url = data.get("url", None)
        title = data.get("title", None)
        if not url or not title:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.add_to_blacklist(request, url, title)
        return JsonResponse({"status": f"Вакансия {url} добавлена в черный список"})

    async def add_to_blacklist(
        self, request: HttpRequest, url: str, title: str
    ) -> None:
        """Асинхронный метод добавления вакансии в черный список.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.
            title (str): Название вакансии.

        Returns:
            None
        """
        try:
            vacancy, created = await UserVacancies.objects.aget_or_create(
                user=request.user, url=url, title=title
            )
            vacancy.is_blacklist = True
            vacancy.save()

            vacancy.is_favourite = False
            vacancy.save()

            logger.info(f"Вакансия {url} добавлена в черный список")
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
        url = data.get("url", None)
        if not url:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)
        await self.delete_from_blacklist(request, url)
        return JsonResponse({"status": f"Вакансия {url} удалена из черного списка"})

    async def delete_from_blacklist(self, request: HttpRequest, url: str) -> None:
        """Асинхронный метод удаления вакансии из черного списка.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.

        Returns:
            None
        """
        try:
            vacancy = await UserVacancies.objects.filter(
                user=request.user, url=url
            ).afirst()
            if not vacancy:
                pass
            elif (
                vacancy.is_blacklist
                and not vacancy.is_favourite
                and not vacancy.hidden_company
            ):
                vacancy.delete()
            else:
                vacancy.is_blacklist = True
                vacancy.save()

            logger.info(f"Вакансия {url} удалена из черного списка")

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
