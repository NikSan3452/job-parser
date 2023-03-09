import json
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from logger import logger, setup_logging
from parser.models import FavouriteVacancy, VacancyBlackList, HiddenCompanies

from .forms import ProfileForm
from .models import Profile, User

# Логирование
setup_logging()


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
    except Exception as exc:
        logger.exception(exc)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile.city = form.cleaned_data["city"].lower()
            profile.job = form.cleaned_data["job"].lower()
            profile.subscribe = form.cleaned_data["subscribe"]
            profile.save()
            logger.debug("Данные профиля сохранены")

            if profile.subscribe:
                messages.success(request, "Вы подписались на рассылку вакансий")
            else:
                messages.error(request, "Вы отписались от рассылки")
            return redirect("profiles:profile", username=username)
    else:
        try:
            favourite_vacancy = FavouriteVacancy.objects.filter(user=user).all()
            black_list = VacancyBlackList.objects.filter(user=user).all()
            hidden_companies = HiddenCompanies.objects.filter(user=user).all()
        except Exception as exc:
            logger.exception(exc)

        default_data = {
            "city": profile.city,
            "job": profile.job,
            "subscribe": profile.subscribe,
        }

        form = ProfileForm(initial=default_data)

    return render(
        request,
        "profiles/profile.html",
        {
            "form": form,
            "user": user,
            "favourite_vacancy": favourite_vacancy,
            "black_list": black_list,
            "hidden_companies": hidden_companies,
        },
    )


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
