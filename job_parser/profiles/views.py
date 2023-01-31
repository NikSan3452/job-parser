from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages, auth

from parser.models import FavouriteVacancy
from .models import Profile, User
from .forms import ProfileForm


@login_required
def profile(request, username):
    user = User.objects.get(username=username)
    profile = Profile.objects.get(user=user)

    if request.method == "POST":
        form = ProfileForm(request.POST)

        if form.is_valid():
            profile.city = form.cleaned_data["city"].lower()
            profile.job = form.cleaned_data["job"].lower()
            profile.subscribe = form.cleaned_data["subscribe"]
            profile.save()
            if profile.subscribe:
                messages.success(request, "Вы подписались на рассылку вакансий")
            else:
                messages.error(request, "Вы отписались от рассылки")
            return redirect("profiles:profile", username=username)
    else:
        try:
            favourite_vacancy = FavouriteVacancy.objects.filter(user=user).all()
        except Exception as exc:
            print(f"Ошибка базы данных {exc}")

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
        },
    )
