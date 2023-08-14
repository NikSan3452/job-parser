from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import FormView
from logger import logger, setup_logging
from parser.models import UserVacancies

from .forms import ProfileForm
from .models import Profile, User

# Логирование
setup_logging()


class ProfileView(LoginRequiredMixin, FormView):
    """Класс представления профиля пользователя.

    Args:
        form_class (ProfileForm): Форма для отображения и обновления данных
        профиля пользователя.
        template_name (str): Имя шаблона для отображения страницы профиля.
    """

    form_class = ProfileForm
    template_name = "profiles/profile.html"

    def get_initial(self) -> dict[str, str]:
        """Возвращает начальные данные для формы.

        Returns:
            dict[str, str]: Словарь с начальными данными для формы.
        """
        initial = super().get_initial()
        self.check_user_permission()
        self.update_initial(initial)
        return initial

    def check_user_permission(self) -> None:
        """Проверяет разрешение пользователя на доступ к странице профиля.

        Raises:
            PermissionDenied: Если имя пользователя в запросе не соответствует имени
            пользователя в параметрах URL.
        """
        if self.request.user.username != self.kwargs["username"]:
            raise PermissionDenied

    def update_initial(self, initial: dict[str, str]) -> None:
        """Обновляет начальные данные формы данными из профиля пользователя.

        Args:
            initial (dict[str, str]): Словарь с начальными данными для формы.

        Raises:
            ObjectDoesNotExist: Если пользователь или профиль не существует.
        """
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

    def get_context_data(self, **kwargs: dict) -> dict[str, str]:
        """Возвращает контекстные данные для отображения страницы профиля.

        Args:
            **kwargs (dict): Дополнительные аргументы.

        Returns:
            dict[str, str]: Словарь с контекстными данными для отображения
            страницы профиля.
        """
        context = super().get_context_data(**kwargs)
        user = self.request.user
        favourite_vacancies, black_list, hidden_companies = self.get_user_vacancies(
            user
        )
        context.update(
            {
                "user": user,
                "favourite_vacancies": favourite_vacancies,
                "black_list": black_list,
                "hidden_companies": hidden_companies,
            }
        )
        return context

    def get_user_vacancies(
        self, user: AbstractBaseUser | AnonymousUser
    ) -> tuple[
        set[UserVacancies] | None,
        set[UserVacancies] | None,
        set[UserVacancies] | None,
    ]:
        """Возвращает списки вакансий пользователя.

        Args:
            user (AbstractBaseUser | AnonymousUser): Пользователь,
            для которого необходимо получить списки вакансий.

        Returns:
            tuple: Кортеж из трех элементов: список избранных вакансий,
            черный список вакансий и список скрытых компаний.

        Raises:
            ObjectDoesNotExist: Если объект не существует.
        """
        favourite_vacancies = None
        black_list = None
        hidden_companies = None
        try:
            user_vacancies = UserVacancies.objects.filter(user=user)
            favourite_vacancies = {
                vacancy for vacancy in user_vacancies if vacancy.is_favourite
            }
            black_list = {vacancy for vacancy in user_vacancies if vacancy.is_blacklist}
            hidden_companies = {
                company for company in user_vacancies if company.hidden_company
            }
        except ObjectDoesNotExist as exc:
            logger.exception(f"Ошибка: {exc} объект не существует")
            raise ObjectDoesNotExist()
        except Exception as exc:
            logger.exception(f"Ошибка: {exc}")
        return favourite_vacancies, black_list, hidden_companies

    def form_valid(self, form: ProfileForm) -> HttpResponseRedirect:
        """Обрабатывает действия при успешной отправке формы.

        Args:
            form (ProfileForm): Форма с данными.

        Returns:
            HttpResponseRedirect: Перенаправление на страницу профиля пользователя.
        """
        profile = self.get_profile()
        self.update_profile(profile, form)
        self.add_message(profile)
        return redirect("profiles:profile", username=self.request.user.username)

    def get_profile(self) -> Profile:
        """Возвращает профиль текущего пользователя.

        Returns:
            Profile: Профиль текущего пользователя.

        Raises:
            ObjectDoesNotExist: Если объект не существует.
        """
        try:
            profile = Profile.objects.get(user=self.request.user)
        except ObjectDoesNotExist as exc:
            logger.exception(f"Ошибка: {exc} объект не существует")
            raise ObjectDoesNotExist()
        except Exception as exc:
            logger.exception(f"Ошибка: {exc}")
        return profile

    def update_profile(self, profile: Profile, form: ProfileForm) -> None:
        """Обновляет данные профиля пользователя.

        Args:
            profile (Profile): Профиль пользователя.
            form (ProfileForm): Форма с данными.
        """
        profile.city = form.cleaned_data["city"].lower()
        profile.job = form.cleaned_data["job"].lower()
        profile.subscribe = form.cleaned_data["subscribe"]
        profile.save()
        logger.debug("Данные профиля сохранены")

    def add_message(self, profile: Profile) -> None:
        """Добавляет сообщение об успешном обновлении данных профиля.

        Args:
            profile (Profile): Профиль пользователя.
        """
        if profile.subscribe:
            messages.success(self.request, "Вы подписались на рассылку вакансий")
        else:
            messages.error(self.request, "Вы отписались от рассылки")
