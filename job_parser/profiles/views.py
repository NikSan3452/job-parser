import json
from parser.models import FavouriteVacancy, HiddenCompanies, VacancyBlackList

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
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


@login_required
def delete_from_blacklist_view(request, username):
    """Удаляет вакансию из черного списка.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    view_logger = logger.bind(request=request.POST)
    if request.method == "POST":

        data = json.load(request)
        vacancy_url = data.get("url")

        try:
            user = auth.get_user(request)
            VacancyBlackList.objects.filter(user=user, url=vacancy_url).delete()
            view_logger.info(f"Вакансия {vacancy_url} удалена из черного списка")
        except Exception as exc:
            view_logger.exception(exc)
    return JsonResponse({"status": f"Вакансия {vacancy_url} удалена из черного списка"})


@login_required
def delete_from_hidden_companies_view(request, username):
    """Удаляет компанию из списка скрытых.

    Args:
        request (_type_): Запрос.

    Returns:
        _type_: JsonResponse.
    """
    view_logger = logger.bind(request=request.POST)
    if request.method == "POST":

        data = json.load(request)
        company = data.get("name")

        try:
            user = auth.get_user(request)
            HiddenCompanies.objects.filter(user=user, name=company).delete()
            view_logger.info(f"Компания {company} удалена из списка скрытых")
        except Exception as exc:
            view_logger.exception(exc)
    return JsonResponse({"status": f"Компания {company} удалена из списка скрытых"})
