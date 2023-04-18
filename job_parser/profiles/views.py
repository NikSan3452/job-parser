import json
from parser.mixins import AsyncLoginRequiredMixin
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import DatabaseError, IntegrityError
from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView
from logger import logger, setup_logging

from .forms import ProfileForm
from .models import Profile, User

# Логирование
setup_logging()


class ProfileView(LoginRequiredMixin, FormView):
    """
    Класс представления для профиля пользователя.

    Этот класс наследуется от LoginRequiredMixin и FormView.
    Требует аутентификации пользователя перед использованием.
    Использует форму ProfileForm и шаблон 'profiles/profile.html'.
    """

    form_class = ProfileForm
    template_name = "profiles/profile.html"

    def get_initial(self) -> dict[str, str]:
        """
        Метод для получения начальных данных формы.

        Этот метод вызывается при создании формы и возвращает словарь с
        начальными данными.
        Начальные данные включают информацию о городе, работе и подписке
        из профиля пользователя.

        Returns:
            dict[str, str]: Словарь с начальными данными формы.
        """
        initial = super().get_initial()
        user = User.objects.get(username=self.kwargs["username"])
        profile = Profile.objects.get(user=user)
        initial.update(
            {
                "city": profile.city,
                "job": profile.job,
                "subscribe": profile.subscribe,
            }
        )
        return initial

    def get_context_data(self, **kwargs: str) -> dict[str, str]:
        """
        Метод для получения контекста данных для шаблона.

        Этот метод вызывается при отображении шаблона и возвращает словарь
        с данными контекста.
        Данные контекста включают информацию о пользователе, избранных вакансиях,
        черном списке вакансий и скрытых компаниях.

        Args:
            **kwargs: Дополнительные аргументы.

        Returns:
            dict[str, str]: Словарь с данными контекста.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update(
            {
                "user": user,
                "favourite_vacancy": FavouriteVacancy.objects.filter(user=user).all(),
                "black_list": VacancyBlackList.objects.filter(user=user).all(),
                "hidden_companies": HiddenCompanies.objects.filter(user=user).all(),
            }
        )
        return context

    def form_valid(self, form: ProfileForm) -> HttpResponseRedirect:
        """
        Метод обработки действительной формы.

        Этот метод вызывается при отправке действительной формы и
        обрабатывает данные формы.
        Данные формы включают информацию о городе, работе и подписке.
        Эти данные сохраняются в профиле пользователя.
        Затем отображается сообщение об успехе или ошибке в зависимости от
        статуса подписки.
        В конце метода происходит перенаправление на страницу профиля пользователя.

        Args:
            form (ProfileForm): Объект формы с данными.

        Returns:
            HttpResponseRedirect: Объект перенаправления на страницу профиля
            пользователя.
        """
        profile = Profile.objects.get(user=self.request.user)
        profile.city = form.cleaned_data["city"].lower()
        profile.job = form.cleaned_data["job"].lower()
        profile.subscribe = form.cleaned_data["subscribe"]
        profile.save()
        logger.debug("Данные профиля сохранены")

        if profile.subscribe:
            messages.success(self.request, "Вы подписались на рассылку вакансий")
        else:
            messages.error(self.request, "Вы отписались от рассылки")
        return redirect("profiles:profile", username=self.request.user.username)


class DeleteFromBlacklistView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления вакансии из черного списка.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest, username: User) -> JsonResponse:
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
        Затем метод пытается удалить объект `VacancyBlackList`
        с указанными данными пользователя и URL вакансии.
        Если все прошло успешно, в лог записывается информация о том,
        что вакансия была удалена из черного списка.
        В случае возникновения исключений DatabaseError или IntegrityError они
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что вакансия была удалена из черного списка.

        Args:
            request (HttpRequest): Объект запроса.
            username (User): Пользователь.

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

            await VacancyBlackList.objects.filter(
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


class DeleteFromHiddenCompaniesView(AsyncLoginRequiredMixin, View):
    """
    Класс представления для удаления компании из списка скрытых.

    Этот класс наследуется от AsyncLoginRequiredMixin и View.
    Требует аутентификации пользователя перед использованием.
    """

    async def post(self, request: HttpRequest, username: User) -> JsonResponse:
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
        записываются в лог и будет возвращен соответствующий JsonResponse со статусом 500.
        В конце метода возвращается JSON-ответ с информацией о том,
        что компания была удалена из списка скрытых.

        Args:
            request (HttpRequest): Объект запроса.
            username (User): Пользователь.

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
