from parser.models import Favourite, HiddenCompanies, BlackList

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseRedirect
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
        начальными данными. В блоке try/except метод пытается получить пользователя,
        а также его профиль. В случае успеха инициирует форму начальными данными.
        Если пользователь или профиль не существуют вызовет исключение
        ObjectDoesNotExist с соответствующей записью в лог.
        Иначе вызовет общее исключение Exception, с записью в лог.
        Начальные данные включают информацию о городе, работе и подписке
        из профиля пользователя. При попытке пользователя просмотреть профиль
        другого пользователя вызовет ошибку PermissionDenied.

        Returns:
            dict[str, str]: Словарь с начальными данными формы.
        """
        initial = super().get_initial()
        if self.request.user.username != self.kwargs["username"]:
            raise PermissionDenied
        try:
            user = User.objects.get(username=self.kwargs["username"])
            profile = Profile.objects.get(user=user)
            initial.update(
                {
                    "city": profile.city,
                    "job": profile.job,
                    "subscribe": profile.subscribe,
                }
            )
        except ObjectDoesNotExist as exc:
            logger.exception(f"Ошибка: {exc} Пользователь или профиль не существует")
            raise ObjectDoesNotExist()
        except Exception as exc:
            logger.exception(f"Ошибка: {exc}")
        return initial

    def get_context_data(self, **kwargs: str) -> dict[str, str]:
        """
        Метод для получения контекста данных для шаблона.

        Этот метод вызывается при отображении шаблона и возвращает словарь
        с данными контекста. В блоке try/except пытается получить вакансии из 
        избранного, вакансии из черного списка и скрытые компании. 
        В случае успеха данные передаются в контекст, а иначе вызывается исключение 
        ObjectDoesNotExist, либо Exception с соответствующей записью в лог.
        Данные контекста включают информацию о пользователе, избранных вакансиях,
        черном списке вакансий и скрытых компаниях.

        Args:
            **kwargs: Дополнительные аргументы.

        Returns:
            dict[str, str]: Словарь с данными контекста.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user

        favourite_vacancy = None
        black_list = None
        hidden_companies = None
        try:
            favourite_vacancy = Favourite.objects.filter(user=user).all()
            black_list = BlackList.objects.filter(user=user).all()
            hidden_companies = HiddenCompanies.objects.filter(user=user).all()
        except ObjectDoesNotExist as exc:
            logger.exception(f"Ошибка: {exc} объект не существует")
            raise ObjectDoesNotExist()
        except Exception as exc:
            logger.exception(f"Ошибка: {exc}")
        context.update(
            {
                "user": user,
                "favourite_vacancy": favourite_vacancy,
                "black_list": black_list,
                "hidden_companies": hidden_companies,
            }
        )
        return context

    def form_valid(self, form: ProfileForm) -> HttpResponseRedirect:
        """
        Метод обработки действительной формы.

        Этот метод вызывается при отправке действительной формы и
        обрабатывает данные формы. В блоке try/except пытается получить
        профиль текущего пользователя и в случае успеха получает данные формы.
        Иначе вызовет исключение ObjectDoesNotExist, либо Exception с соответствующей
        записью в лог.
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
        try:
            profile = Profile.objects.get(user=self.request.user)
        except ObjectDoesNotExist as exc:
            logger.exception(f"Ошибка: {exc} объект не существует")
            raise ObjectDoesNotExist()
        except Exception as exc:
            logger.exception(f"Ошибка: {exc}")

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
