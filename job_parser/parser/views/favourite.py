from parser.mixins import AsyncLoginRequiredMixin
from parser.models import UserVacancies, Vacancies
from parser.utils import Utils

from django.db import DatabaseError
from django.http import HttpRequest, JsonResponse
from django.views import View
from logger import logger, setup_logging

# Логирование
setup_logging()


class AddToFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для добавления вакансии в избранное.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на добавление вакансии в список избранных.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном добавлении вакансии
            в список избранного.
        """
        data = Utils.get_data(request)
        pk = data.get("pk", None)
        if not pk:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        await self.add_to_favourite(request, pk)
        return JsonResponse({"status": f"Вакансия {pk} добавлена в избранное"})

    async def add_to_favourite(self, request: HttpRequest, pk: str) -> None:
        """Асинхронный метод добавления вакансии в базу данных.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.
            title (str): Название вакансии.

        Returns: None
        """
        try:
            vacancy = await Vacancies.objects.aget(pk=pk)
            user_vacancy, created = await UserVacancies.objects.aget_or_create(
                user=request.user, vacancy=vacancy
            )
            if not user_vacancy.is_blacklist or not user_vacancy.hidden_company:
                user_vacancy.is_favourite = True
                user_vacancy.save()

            logger.info(f"Вакансия {pk} добавлена в избранное")

        except Exception as exc:
            logger.exception(exc)


class DeleteFromFavouritesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из списка избранных.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на удаление вакансии из списка избранных.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об успешном удалении вакансии
            из списка избранного.
        """
        data = Utils.get_data(request)
        pk = data.get("pk", None)
        if not pk:
            return JsonResponse({"Ошибка": "Невалидный JSON"}, status=400)

        await self.delete_from_favourite(request, pk)
        return JsonResponse({"status": f"Вакансия {pk} удалена из избранного"})

    async def delete_from_favourite(self, request: HttpRequest, pk: str) -> None:
        """Асинхронный метод удаления вакансии из базы данных.

        Args:
            request (HttpRequest): Объект запроса.
            url (str): URL вакансии.

        Returns: None
        """
        try:
            vacancy = await Vacancies.objects.aget(pk=pk)
            user_vacancy = await UserVacancies.objects.filter(
                user=request.user, vacancy=vacancy
            ).afirst()
            if not user_vacancy:
                pass
            elif user_vacancy.is_blacklist or user_vacancy.hidden_company:
                user_vacancy.is_favourite = False
            else:
                user_vacancy.delete()
                logger.info(f"Вакансия {pk} удалена из избранного")
        except Exception as exc:
            logger.exception(exc)


class ClearFavouriteList(AsyncLoginRequiredMixin, View):
    """
    Класс представления для очистки списка избранных вакансий.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest) -> JsonResponse:
        """Метод обработки POST-запроса на очистку списка избранных вакансий.

        Args:
            request (HttpRequest): Объект запроса.

        Returns:
            JsonResponse: JSON-ответ с информацией об
            успешной очистке списка избранного.
        """
        try:
            vacancies = UserVacancies.objects.filter(user=request.user)
            for vacancy in vacancies:
                if vacancy.is_blacklist or vacancy.hidden_company:
                    vacancy.is_favourite = False
                    vacancy.save()
                else:
                    vacancy.delete()
            logger.info("Список избранных вакансий успешно очищен")
        except DatabaseError as exc:
            logger.exception(exc)
            return JsonResponse({"Ошибка": "Произошла ошибка базы данных"}, status=500)

        return JsonResponse({"status": "Список избранных вакансий успешно очищен"})
